"""Score every forecast of the daily extremes against the realised 15-min extremes.

Reads:  models/{CC}_direct.csv       (output of 2_run_models.py)
Writes: results/extremes_errors.csv  one row per (country, forecaster, target,
        horizon) with n, mae, rmse; horizon "avg" pools h3-h9

Forecasters:
  tso                  the TSO's A31 week-ahead daily min/max forecast
  direct_{scenario}    the min/max regressions and the two benchmarks

The truth is the daily min/max of the 15-min load, which is what the TSO
measures and publishes against.
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


def evaluate_country(cc: str) -> pd.DataFrame:
    """Long MAE/RMSE table for one market."""
    direct = pd.read_csv(MODELS_DIR / f"{cc}_direct.csv")
    frame = direct.rename(columns={"tso_prediction": "tso", **{c: "direct_" + c.removesuffix("_prediction") for c in scenario_columns(direct)}})

    forecasters = [c for c in frame.columns if c == "tso" or c.startswith("direct_")]
    long = frame.melt(id_vars=[*ON, "actual"], value_vars=forecasters, var_name="forecaster", value_name="prediction").dropna(subset=["prediction", "actual"])
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
            print(f"skip {cc}: no predictions (run 2_run_models.py first)")
            continue
        table = evaluate_country(cc)
        table.insert(0, "country", cc)
        tables.append(table)
        headline = table[table.horizon == "avg"].groupby("forecaster")["mae"].mean()
        print(f"{cc}  " + "  ".join(f"{f}={m:.1f}" for f, m in headline.items()))

    if not tables:
        return
    out = pd.concat(tables, ignore_index=True)[["country", "forecaster", "target", "horizon", "n", "mae", "rmse"]]
    out.to_csv(OUT_PATH, index=False, float_format="%.2f")
    print(f"saved {OUT_PATH}  ({len(out)} rows)")


if __name__ == "__main__":
    main()
