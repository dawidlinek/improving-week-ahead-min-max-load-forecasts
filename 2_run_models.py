"""Fit one rolling-window LassoCV per (country, scenario, week, horizon, target)

Reads:  data/features/data_{CC}.csv  (output of 1d_prepare_features.py)
Writes: models/{CC}_direct.csv        one row per (run_date, horizon 3-9, target min/max)
        models/{CC}_direct_coefs.csv  one row per (fit, nonzero term)
        models/{CC}_direct_fits.csv   one row per fit (alpha, sparsity, target scaling)

The forecast file has run_date, target_date, horizon, target, actual,
tso_prediction (the A31 week-ahead benchmark), and one {scenario}_prediction
column per scenario and per BENCHMARKS entry (unbiased, expert).

Usage: python 2_run_models.py [--countries PT DE ...]
"""

import argparse
import os
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.linear_model import LassoCV, LinearRegression
from sklearn.preprocessing import StandardScaler

from country_config import COUNTRIES
from model_config import (TRAINING_WINDOW, TEST_START, TEST_END, HORIZONS, TARGETS, EXTREME, TSO_EXTREME,
                          SCENARIOS, BENCHMARKS, expand_target)

ROOT         = Path(__file__).parent
FEATURES_DIR = ROOT / "data" / "features"
MODELS_DIR   = ROOT / "models"
SHARD_DIR    = MODELS_DIR / "coefs_shards"
NAN          = float("nan")


def load_features(cc: str) -> pd.DataFrame:
    df = pd.read_csv(FEATURES_DIR / f"data_{cc}.csv", index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(COUNTRIES[cc]["tz"])
    return df


def lasso_coefficients(model, scaler_x, scaler_y, columns) -> list[tuple[str, float, float]]:
    """Map a LassoCV fitted on standardised data back to raw units. """
    w = model.coef_
    y_mean, y_std = float(scaler_y.mean_[0]), float(scaler_y.scale_[0])
    nz = np.flatnonzero(w)
    beta = w[nz] * y_std / scaler_x.scale_[nz]
    intercept = y_mean - float(np.dot(beta, scaler_x.mean_[nz]))
    return [("intercept", intercept, 0.0)] + [(columns[j], float(b), float(w[j])) for j, b in zip(nz, beta)]


def fit_scenario(df: pd.DataFrame, template: list[str], estimator: str = "lasso"):
    """Rolling-window fit over every (horizon, week, target)."""
    days = df["day"]
    test_start_day = int(df.loc[df.index.date >= pd.Timestamp(TEST_START).date(), "day"].iloc[0])
    test_end_day   = int(df.loc[df.index.date <= pd.Timestamp(TEST_END).date(),   "day"].iloc[-1])

    records: list[dict] = []
    coefs:   list[dict] = []
    fits:    list[dict] = []
    for hz in HORIZONS:
        preds_by_key = {key: expand_target(template, hz, key) for key in TARGETS}

        for day_val in range(test_start_day, test_end_day + 1, 7):
            mask   = (days >= day_val - TRAINING_WINDOW - hz) & (days <= day_val)
            window = df[mask]

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
                        designs[ck] = (train_x, test_x, scaler_x.fit_transform(train_x), scaler_x.transform(test_x), scaler_x)
                    else:
                        designs[ck] = (train_x, test_x, None, None, None)
                return designs[ck]

            for key in TARGETS:
                train_x, test_x, train_x_sc, test_x_sc, scaler_x = design(preds_by_key[key])

                target_col = EXTREME.format(hz=hz, key=key)
                train_y = window[target_col].loc[train_x.index]
                actual  = window[target_col].iloc[-1]

                valid = train_y.notna().values
                alpha = NAN
                if estimator == "offset":
                    beta0 = float((train_y[valid] - train_x.iloc[:, 0][valid]).mean())
                    pred  = float(test_x.iloc[0, 0]) + beta0
                    # Slope is fixed at 1 rather than fitted; recorded so that
                    # the export reconstructs the prediction like any other model.
                    fitted = [("intercept", beta0, NAN), (train_x.columns[0], 1.0, NAN)]
                elif estimator == "ols":
                    model = LinearRegression()
                    model.fit(train_x[valid], train_y[valid])
                    pred = float(model.predict(test_x)[0])
                    fitted = [("intercept", float(model.intercept_), NAN)] + [(p, float(c), NAN) for p, c in zip(train_x.columns, model.coef_)]
                else:
                    scaler_y   = StandardScaler()
                    train_y_sc = scaler_y.fit_transform(train_y[valid].values.reshape(-1, 1)).ravel()

                    model = LassoCV(fit_intercept=False, max_iter=100000, cv=7)
                    model.fit(train_x_sc[valid], train_y_sc)
                    pred = float(scaler_y.inverse_transform(model.predict(test_x_sc).reshape(-1, 1))[0, 0])
                    fitted = lasso_coefficients(model, scaler_x, scaler_y, list(train_x.columns))
                    alpha = float(model.alpha_)

                run_date = test_x.index[0].normalize()
                records.append({
                    "date":       run_date,
                    "horizon":    hz,
                    "target":     key,
                    "actual":     float(actual),
                    "prediction": pred,
                    "tso":        float(window[TSO_EXTREME.format(hz=hz, key=key)].iloc[-1]),
                })

                ident = {"run_date": run_date.date(), "horizon": hz, "target": key}
                coefs += [{**ident, "term": t, "beta": b, "beta_std": bs} for t, b, bs in fitted]
                y_valid = train_y[valid].values
                fits.append({**ident, "estimator": estimator, "alpha": alpha,
                             "n_nonzero": sum(t != "intercept" for t, _, _ in fitted),
                             "n_train": int(valid.sum()),
                             "y_mean": float(y_valid.mean()), "y_std": float(y_valid.std())})

    return pd.DataFrame(records), pd.DataFrame(coefs), pd.DataFrame(fits)


def merge_scenarios(scenario_dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Combine per-scenario long predictions into one table: one row per
    (run_date, horizon, target), one prediction column per scenario."""
    names = list(scenario_dfs)
    on = ["date", "horizon", "target"]

    out = scenario_dfs[names[0]].rename(columns={"prediction": f"{names[0]}_prediction"})
    for n in names[1:]:
        right = scenario_dfs[n][on + ["prediction"]].rename(columns={"prediction": f"{n}_prediction"})
        out = out.merge(right, on=on, how="left")

    out = out.rename(columns={"date": "run_date", "tso": "tso_prediction"})
    out["run_date"]    = out["run_date"].dt.tz_localize(None).dt.normalize()
    out["target_date"] = (out["run_date"] + pd.to_timedelta(out["horizon"], unit="D")).dt.date
    out["run_date"]    = out["run_date"].dt.date

    ordered = ["run_date", "target_date", "horizon", "target", "actual", "tso_prediction"] + [f"{n}_prediction" for n in names]
    return out[ordered].sort_values(["run_date", "horizon", "target"]).reset_index(drop=True)


def fit_one(cc: str, scenario: str, template: list[str], estimator: str):
    """One fit task: every (week, horizon, target) of one country-scenario."""
    df = load_features(cc)
    predictions, coefs, fits = fit_scenario(df, template, estimator)
    SHARD_DIR.mkdir(parents=True, exist_ok=True)
    for kind, frame in (("coefs", coefs), ("fits", fits)):
        frame.insert(0, "model", scenario)
        frame.to_csv(SHARD_DIR / f"{cc}_direct_{scenario}_{kind}.csv", index=False, float_format="%.10g")
    return cc, scenario, predictions


def collect_shards(cc: str) -> None:
    """Concatenate one country's coefficient shards and delete them."""
    for kind in ("coefs", "fits"):
        shards = sorted(SHARD_DIR.glob(f"{cc}_direct_*_{kind}.csv"))
        if not shards:
            continue
        frame = pd.concat([pd.read_csv(p) for p in shards], ignore_index=True)
        out_path = MODELS_DIR / f"{cc}_direct_{kind}.csv"
        frame.to_csv(out_path, index=False, float_format="%.10g")
        print(f"saved {out_path}  ({len(frame):,} rows)")
        for p in shards:
            p.unlink()


def missing_predictors(todo: list[tuple]) -> dict[tuple[str, str], list[str]]:
    columns: dict[str, set[str]] = {}
    missing: dict[tuple[str, str], list[str]] = {}
    for cc, scenario, template, _ in todo:
        if cc not in columns:
            columns[cc] = set(pd.read_csv(FEATURES_DIR / f"data_{cc}.csv", nrows=0).columns)
        need = {p for hz in HORIZONS for key in TARGETS for p in expand_target(template, hz, key)}
        if need - columns[cc]:
            missing[(cc, scenario)] = sorted(need - columns[cc])
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--countries", nargs="*", metavar="CC", default=list(COUNTRIES))
    args = parser.parse_args()

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    todo = []
    for cc in args.countries:
        if not (FEATURES_DIR / f"data_{cc}.csv").exists():
            print(f"skip {cc}: no feature file (run 1d_prepare_features.py first)")
            continue
        if (MODELS_DIR / f"{cc}_direct.csv").exists():
            print(f"skip {cc}: output already exists (delete it to refit)")
            continue
        todo += [(cc, scenario, template, "lasso") for scenario, template in SCENARIOS.items()]
        todo += [(cc, bench, spec["predictors"], spec["estimator"]) for bench, spec in BENCHMARKS.items()]
    if not todo:
        return
    missing = missing_predictors(todo)
    if missing:
        for (cc, scenario), cols in missing.items():
            print(f"{cc} {scenario}: {len(cols)} predictor columns missing, e.g. {', '.join(cols[:3])}")
        raise SystemExit("the feature frames lack predictors these scenarios use; rebuild them with "
                         "1c_download_load.py and 1d_prepare_features.py instead of fitting on fewer predictors")

    n_cores = os.cpu_count() or 1
    n_jobs  = min(len(todo), n_cores)

    started_at = time.time()
    print(f"fitting {len(todo)} tasks on {n_jobs} of {n_cores} cores")
    results = Parallel(n_jobs=n_jobs, backend="loky", inner_max_num_threads=1, verbose=10)(delayed(fit_one)(*task) for task in todo)
    print(f"=== all fits done in {time.time() - started_at:.0f}s ===")

    grouped: dict[str, dict[str, pd.DataFrame]] = defaultdict(dict)
    for cc, scenario, predictions in results:
        grouped[cc][scenario] = predictions

    for cc, scenario_dfs in grouped.items():
        merged = merge_scenarios(scenario_dfs)
        out_path = MODELS_DIR / f"{cc}_direct.csv"
        merged.to_csv(out_path, index=False, float_format="%.3f")
        print(f"saved {out_path}  ({len(merged)} rows, {len(merged.columns)} cols)")
        collect_shards(cc)

    if SHARD_DIR.exists() and not any(SHARD_DIR.iterdir()):
        SHARD_DIR.rmdir()


if __name__ == "__main__":
    main()
