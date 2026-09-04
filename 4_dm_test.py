r"""Diebold-Mariano significance test of each model against the raw TSO forecast,
one test per (country, forecaster, target, horizon), direct route only.

Reads:  models/{CC}_direct.csv        (output of 2_run_models.py)
Writes: results/dm_significance.csv   long format, one row per
        (country, forecaster, target, horizon) with p_value, stars.

This is the univariate DM test exactly as implemented in epftoolbox.evaluation.DM
(Lago, Marcjasz, De Schutter and Weron 2021 -- \citep{lag:etal:21}

    https://github.com/jeslago/epftoolbox/blob/master/epftoolbox/evaluation/_dm.py

We swap 24h split into 7 horizons split
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm as norm_dist

from country_config import COUNTRIES
from model_config import BENCHMARKS, SCENARIOS

ROOT       = Path(__file__).parent
MODELS_DIR = ROOT / "models"
OUT_PATH   = ROOT / "results" / "dm_significance.csv"

FORECASTERS = list(BENCHMARKS) + list(SCENARIOS)   # unbiased, expert, base, capital_temperature, regional_nwp
TARGETS     = ("min", "max")


# ── the test itself (epftoolbox.evaluation.DM, version='univariate') ────────
def DM(p_real: np.ndarray, p_pred_1: np.ndarray, p_pred_2: np.ndarray, norm: int = 1) -> np.ndarray:
    e1 = p_real - p_pred_1
    e2 = p_real - p_pred_2
    d = np.abs(e1) - np.abs(e2)
    N = d.shape[0]
    mean_d = d.mean(axis=0)
    var_d = d.var(axis=0, ddof=0)
    dm_stat = mean_d / np.sqrt(var_d / N)
    return 1 - norm_dist.cdf(dm_stat)


def stars(p: float) -> str:
    if not np.isfinite(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


# ── per-country evaluation ───────────────────────────────────────────────────
def evaluate_country(cc: str) -> pd.DataFrame:
    df = pd.read_csv(MODELS_DIR / f"{cc}_direct.csv")
    rows = []
    for target in TARGETS:
        sub = df[df["target"] == target]
        actual = sub.pivot(index="run_date", columns="horizon", values="actual").sort_index(axis=1)
        tso    = sub.pivot(index="run_date", columns="horizon", values="tso_prediction").sort_index(axis=1)
        horizons = actual.columns.to_numpy()
        for forecaster in FORECASTERS:
            model = sub.pivot(index="run_date", columns="horizon",
                              values=f"{forecaster}_prediction").sort_index(axis=1)
            p_values = DM(actual.to_numpy(), tso.to_numpy(), model.to_numpy(), norm=1)
            for h, p in zip(horizons, p_values):
                rows.append({
                    "country": cc, "forecaster": forecaster, "target": target,
                    "horizon": int(h), "n": len(actual), "p_value": float(p), "stars": stars(p),
                })
    return pd.DataFrame(rows)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tables = []
    for cc in COUNTRIES:
        if not (MODELS_DIR / f"{cc}_direct.csv").exists():
            print(f"skip {cc}: no direct predictions (run 2_run_models.py first)")
            continue
        tables.append(evaluate_country(cc))
    if not tables:
        return
    out = pd.concat(tables, ignore_index=True)
    out.to_csv(OUT_PATH, index=False, float_format="%.4f")
    print(f"saved {OUT_PATH}  ({len(out)} rows)")

    n = len(out)
    for thresh, label in ((0.10, "p<0.10"), (0.05, "p<0.05"), (0.01, "p<0.01")):
        sig = (out["p_value"] < thresh).sum()
        print(f"{label}: {sig}/{n} cells significant ({100*sig/n:.1f}%)")


if __name__ == "__main__":
    main()
