"""Score every way of forecasting the daily extremes against the same truth.

Reads:  models/{CC}_direct.csv and models/{CC}_profile.csv  (output of 2)
Writes: results/extremes_errors.csv  -- long format, one row per
        (country, forecaster, target, horizon) with n, mae, rmse;
        horizon "avg" pools h3-h9.

Forecasters:
  tso                  the TSO's A31 week-ahead daily min/max forecast
  direct_{scenario}    the direct min/max regressions
  derived_{scenario}   min/max of the profile readout's predicted 24-hour curve

All are scored against the 15-min daily extremes carried in the direct file
(the TSO's operational measurement) on h3-h9, the horizons all of them cover.
Derived extremes come from hourly-mean curves and therefore carry a structural
smoothing handicap versus a 15-min truth; this table measures it.
"""

from pathlib import Path

import pandas as pd

from country_config import COUNTRIES

ROOT       = Path(__file__).parent
MODELS_DIR = ROOT / "models"
OUT_PATH   = ROOT / "results" / "extremes_errors.csv"

ON = ["run_date", "horizon", "target"]


def scenario_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.endswith("_prediction") and c != "tso_prediction"]


def derived_extremes(profile: pd.DataFrame) -> pd.DataFrame:
    """Min and max of each scenario's predicted 24-hour curve, long by target."""
    preds = scenario_columns(profile)
    grouped = profile.groupby(["run_date", "horizon"])[preds]
    parts = []
    for target, agg in (("min", grouped.min()), ("max", grouped.max())):
        part = agg.rename(columns=lambda c: "derived_" + c.removesuffix("_prediction")).reset_index()
        part["target"] = target
        parts.append(part)
    return pd.concat(parts)


def evaluate_country(cc: str) -> pd.DataFrame:
    direct = pd.read_csv(MODELS_DIR / f"{cc}_direct.csv")
    frame = direct.rename(columns={"tso_prediction": "tso", **{c: "direct_" + c.removesuffix("_prediction") for c in scenario_columns(direct)}})

    profile_path = MODELS_DIR / f"{cc}_profile.csv"
    if profile_path.exists():
        frame = frame.merge(derived_extremes(pd.read_csv(profile_path)), on=ON, how="left")

    forecasters = [c for c in frame.columns if c == "tso" or c.startswith(("direct_", "derived_"))]
    long = frame.melt(id_vars=[*ON, "actual"], value_vars=forecasters, var_name="forecaster", value_name="prediction").dropna(subset=["prediction"])
    long["abs_err"] = (long["prediction"] - long["actual"]).abs()
    long["sq_err"]  = (long["prediction"] - long["actual"]) ** 2

    def summarize(df: pd.DataFrame, horizon) -> pd.DataFrame:
        out = df.groupby(["forecaster", "target"], as_index=False).agg(n=("abs_err", "size"), mae=("abs_err", "mean"), mse=("sq_err", "mean"))
        out["rmse"] = out.pop("mse") ** 0.5
        out["horizon"] = horizon
        return out

    per_horizon = [summarize(g, hz) for hz, g in long.groupby("horizon")]
    return pd.concat([*per_horizon, summarize(long, "avg")], ignore_index=True)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    tables = []
    for cc in COUNTRIES:
        if not (MODELS_DIR / f"{cc}_direct.csv").exists():
            print(f"skip {cc}: no direct predictions (run 2_run_models.py first)")
            continue
        table = evaluate_country(cc)
        table.insert(0, "country", cc)
        tables.append(table)
        headline = table[(table.horizon == "avg")].groupby("forecaster")["mae"].mean()
        print(f"{cc}  " + "  ".join(f"{f}={m:.1f}" for f, m in headline.items()))

    if not tables:
        return
    out = pd.concat(tables, ignore_index=True)
    out = out[["country", "forecaster", "target", "horizon", "n", "mae", "rmse"]]
    out.to_csv(OUT_PATH, index=False, float_format="%.2f")
    print(f"saved {OUT_PATH}  ({len(out)} rows)")


if __name__ == "__main__":
    main()
