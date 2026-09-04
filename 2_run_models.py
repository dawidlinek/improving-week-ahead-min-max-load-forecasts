"""Fit one rolling-window LassoCV per (country, scenario, week, horizon, stream)

Reads:  data/features/data_{CC}.csv  (output of 1d_prepare_features.py)
Writes: models/{CC}_direct.csv       one row per (run_date, horizon 3-9, target min/max)
        models/{CC}_profile.csv      one row per (run_date, horizon 3-9, hour 0-23)

Both files share the schema: run_date, target_date, horizon, <target|hour>,
actual, {scenario}_prediction per fitted scenario. The direct file also has
tso_prediction (the A31 week-ahead benchmark) plus one column per BENCHMARKS
entry (unbiased, expert -- simple reference models with target-specific
predictors, coefficients saved to models/{CC}_bench_params.csv); the profile
file has no TSO column since the TSO publishes no hourly forecast at these
horizons.

The two readouts share everything -- rolling window, leakage guard, scaling,
LassoCV -- and differ only in the target columns they regress on (READOUTS in
model_config.py).

Usage: python 2_run_models.py [--readout direct|profile|both] [--countries PT DE ...]
"""

import argparse
import os
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd
from joblib import Parallel, delayed
from sklearn.linear_model import LassoCV, LinearRegression
from sklearn.preprocessing import StandardScaler

from country_config import COUNTRIES
from model_config import (TRAINING_WINDOW, TEST_START, TEST_END, HORIZONS, READOUTS, SCENARIOS, BENCHMARKS,
                          expand_target)

ROOT         = Path(__file__).parent
FEATURES_DIR = ROOT / "data" / "features"
MODELS_DIR   = ROOT / "models"


def load_features(cc: str) -> pd.DataFrame:
    df = pd.read_csv(FEATURES_DIR / f"data_{cc}.csv", index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(COUNTRIES[cc]["tz"])
    return df


def fit_scenario(df: pd.DataFrame, template: list[str], ro: dict, estimator: str = "lasso"):
    """Rolling-window fit over every (horizon, week, stream) of one readout.
    Returns (records, params): records is the long prediction frame (date,
    horizon, <key>, actual, prediction, tso); params holds the fitted
    coefficients per (date, horizon, key, term) for the non-lasso estimators
    (None for lasso).

    Scenario templates share one design matrix across streams; benchmark
    templates reference "{key}" and get a target-specific design per stream.
    estimator: "lasso" (standardised LassoCV), "ols" (OLS + intercept), or
    "offset" (slope fixed at 1 on the single predictor, fitted intercept)."""
    days = df["day"]
    test_start_day = int(df.loc[df.index.date >= pd.Timestamp(TEST_START).date(), "day"].iloc[0])
    test_end_day   = int(df.loc[df.index.date <= pd.Timestamp(TEST_END).date(),   "day"].iloc[-1])

    records: list[dict] = []
    params:  list[dict] = []
    for hz in HORIZONS:
        preds_by_key = {key: [p for p in expand_target(template, hz, key) if p in df.columns]
                        for key in ro["keys"]}

        for day_val in range(test_start_day, test_end_day + 1, 7):
            mask   = (days >= day_val - TRAINING_WINDOW - hz) & (days <= day_val)
            window = df[mask]

            # One design (and scaler fit) per distinct predictor set: scenario
            # streams all hit the same cache entry, benchmark streams one each.
            designs: dict[tuple, tuple] = {}

            def design(preds: list[str]) -> tuple:
                ck = tuple(preds)
                if ck not in designs:
                    x_full  = window[preds]
                    # Target leak move back
                    train_x = x_full.iloc[:-(1 + hz)]
                    train_x = train_x[~train_x.isna().any(axis=1)]
                    test_x  = x_full.iloc[[-1]]
                    if estimator == "lasso":
                        scaler_x = StandardScaler()
                        designs[ck] = (train_x, test_x, scaler_x.fit_transform(train_x), scaler_x.transform(test_x))
                    else:
                        designs[ck] = (train_x, test_x, None, None)
                return designs[ck]

            for key in ro["keys"]:
                train_x, test_x, train_x_sc, test_x_sc = design(preds_by_key[key])

                target_col    = ro["target"].format(hz=hz, key=key)
                benchmark_col = ro["benchmark"] and ro["benchmark"].format(hz=hz, key=key)

                train_y = window[target_col].loc[train_x.index]
                actual  = window[target_col].iloc[-1]

                valid = train_y.notna().values
                fitted: dict[str, float] = {}
                if estimator == "offset":
                    beta0 = float((train_y[valid] - train_x.iloc[:, 0][valid]).mean())
                    pred  = float(test_x.iloc[0, 0]) + beta0
                    fitted = {"intercept": beta0}
                elif estimator == "ols":
                    model = LinearRegression()
                    model.fit(train_x[valid], train_y[valid])
                    pred = float(model.predict(test_x)[0])
                    fitted = {"intercept": float(model.intercept_),
                              **{p: float(c) for p, c in zip(train_x.columns, model.coef_)}}
                else:
                    scaler_y   = StandardScaler()
                    train_y_sc = scaler_y.fit_transform(train_y[valid].values.reshape(-1, 1)).ravel()

                    model = LassoCV(fit_intercept=False, max_iter=100000, cv=7)
                    model.fit(train_x_sc[valid], train_y_sc)
                    pred = float(scaler_y.inverse_transform(model.predict(test_x_sc).reshape(-1, 1))[0, 0])

                records.append({
                    "date":       test_x.index[0].normalize(),
                    "horizon":    hz,
                    ro["key"]:    key,
                    "actual":     float(actual),
                    "prediction": pred,
                    "tso":        float(window[benchmark_col].iloc[-1]) if benchmark_col else float("nan"),
                })
                params += [{"run_date": test_x.index[0].normalize().date(), "horizon": hz,
                            ro["key"]: key, "term": t, "value": v} for t, v in fitted.items()]

    return pd.DataFrame(records), (pd.DataFrame(params) if params else None)


def merge_scenarios(scenario_dfs: dict[str, pd.DataFrame], key: str) -> pd.DataFrame:
    """Combine per-scenario long predictions into one table: one row per
    (run_date, horizon, key), one prediction column per scenario."""
    names = list(scenario_dfs)
    on = ["date", "horizon", key]

    out = scenario_dfs[names[0]].rename(columns={"prediction": f"{names[0]}_prediction"})
    for n in names[1:]:
        right = scenario_dfs[n][on + ["prediction"]].rename(columns={"prediction": f"{n}_prediction"})
        out = out.merge(right, on=on, how="left")

    out = out.rename(columns={"date": "run_date", "tso": "tso_prediction"})
    out["target_date"] = out["run_date"] + pd.to_timedelta(out["horizon"], unit="D")
    out["run_date"]    = out["run_date"].dt.tz_localize(None).dt.date
    out["target_date"] = out["target_date"].dt.tz_localize(None).dt.date

    benchmark = [] if out["tso_prediction"].isna().all() else ["tso_prediction"]
    ordered = ["run_date", "target_date", "horizon", key, "actual", *benchmark] + [f"{n}_prediction" for n in names]
    return out[ordered].sort_values(["run_date", "horizon", key]).reset_index(drop=True)


def fit_one(cc: str, readout_name: str, scenario: str, template: list[str], estimator: str = "lasso"):
    df = load_features(cc)
    predictions, params = fit_scenario(df, template, READOUTS[readout_name], estimator)
    if params is not None:
        params.insert(0, "model", scenario)
    return cc, readout_name, scenario, predictions, params


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readout", choices=[*READOUTS, "both"], default="both")
    parser.add_argument("--countries", nargs="*", metavar="CC", default=list(COUNTRIES))
    args = parser.parse_args()
    readouts = list(READOUTS) if args.readout == "both" else [args.readout]

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    todo = []
    for cc in args.countries:
        if not (FEATURES_DIR / f"data_{cc}.csv").exists():
            print(f"skip {cc}: no feature file (run 1d_prepare_features.py first)")
            continue
        for name in readouts:
            if (MODELS_DIR / f"{cc}_{name}.csv").exists():
                print(f"skip {cc} {name}: output already exists (delete it to refit)")
                continue
            todo += [(cc, name, scenario, template, "lasso") for scenario, template in SCENARIOS.items()]
            if name == "direct":
                todo += [(cc, name, bench, spec["predictors"], spec["estimator"])
                         for bench, spec in BENCHMARKS.items()]
    if not todo:
        return

    # Split the core budget across workers
    n_cores = os.cpu_count() or 1
    n_jobs  = min(len(todo), n_cores)
    inner   = max(1, n_cores // n_jobs)

    started_at = time.time()
    print(f"fitting {len(todo)} tasks: n_jobs={n_jobs} x inner_threads={inner} on {n_cores} cores")
    results = Parallel(n_jobs=n_jobs, backend="loky", inner_max_num_threads=1, verbose=10)(delayed(fit_one)(*task) for task in todo)
    print(f"=== all fits done in {time.time() - started_at:.0f}s ===")

    grouped: dict[tuple[str, str], dict[str, pd.DataFrame]] = defaultdict(dict)
    all_params: dict[str, list[pd.DataFrame]] = defaultdict(list)
    for cc, name, scenario, predictions, params in results:
        grouped[(cc, name)][scenario] = predictions
        if params is not None:
            all_params[cc].append(params)

    for (cc, name), scenario_dfs in grouped.items():
        merged = merge_scenarios(scenario_dfs, READOUTS[name]["key"])
        out_path = MODELS_DIR / f"{cc}_{name}.csv"
        merged.to_csv(out_path, index=False, float_format="%.3f")
        print(f"saved {out_path}  ({len(merged)} rows, {len(merged.columns)} cols)")

    for cc, frames in all_params.items():
        out_path = MODELS_DIR / f"{cc}_bench_params.csv"
        pd.concat(frames).to_csv(out_path, index=False, float_format="%.4f")
        print(f"saved {out_path}")


if __name__ == "__main__":
    main()
