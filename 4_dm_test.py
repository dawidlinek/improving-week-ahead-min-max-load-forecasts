r"""One-sided Diebold-Mariano tests of each model against the raw TSO forecast.

Reads:  models/{CC}_direct.csv         (output of 2_run_models.py)
Writes: results/dm_significance.csv    one row per (country, forecaster, target,
        horizon) with the DM statistic, its p-value and significance stars

The test is the univariate DM test of Diebold and Mariano (1995), in the form
implemented in epftoolbox.evaluation.DM (Lago, Marcjasz, De Schutter and Weron
2021)

    https://github.com/jeslago/epftoolbox/blob/master/epftoolbox/evaluation/_dm.py

with the 24h split swapped for a 7-horizon one, and with ONE deliberate
departure: the variance of the mean loss differential is the Newey-West
heteroskedasticity and autocorrelation consistent estimator (Bartlett kernel,
truncation lag of 4 weeks), not the package's i.i.d. sample variance.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm as norm_dist

from country_config import COUNTRIES
from model_config import BENCHMARKS, SCENARIOS, TARGETS

ROOT       = Path(__file__).parent
MODELS_DIR = ROOT / "models"
OUT_DIR    = ROOT / "results"

FORECASTERS = list(BENCHMARKS) + list(SCENARIOS)   # unbiased, expert, then the scenarios
HAC_LAGS    = 4                                    # weeks of dependence in the Newey-West variance


# ── the test itself (epftoolbox.evaluation.DM) ──────────────────────────────
def loss_differential(p_real: np.ndarray, p_pred_1: np.ndarray, p_pred_2: np.ndarray) -> np.ndarray:
    """|error of forecast 1| - |error of forecast 2|, positive where 2 is better."""
    return np.abs(p_real - p_pred_1) - np.abs(p_real - p_pred_2)


def hac_variance(d: np.ndarray, lags: int) -> np.ndarray:
    """Bartlett-kernel long-run variance of each column of d."""
    n = d.shape[0]
    dev = d - d.mean(axis=0)
    omega = (dev ** 2).mean(axis=0)
    for j in range(1, lags + 1):
        omega += 2 * (1 - j / (lags + 1)) * (dev[j:] * dev[:-j]).sum(axis=0) / n
    return omega


def dm_pvalue(d: np.ndarray, lags: int = HAC_LAGS) -> tuple[np.ndarray, np.ndarray]:
    """One-sided DM statistic and p-value per column of d, with the HAC variance."""
    n = d.shape[0]
    dm_stat = d.mean(axis=0) / np.sqrt(hac_variance(d, lags) / n)
    return dm_stat, 1 - norm_dist.cdf(dm_stat)


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
def evaluate_country(cc: str, reference: str = "tso") -> pd.DataFrame:
    df = pd.read_csv(MODELS_DIR / f"{cc}_direct.csv")
    present = [c.removesuffix("_prediction") for c in df.columns if c.endswith("_prediction")]
    if reference not in present:
        raise SystemExit(f"{cc}: no {reference}_prediction column in {MODELS_DIR}")
    forecasters = [f for f in FORECASTERS if f in present]
    if reference != "tso":
        forecasters = ["tso"] + [f for f in forecasters if f != reference]
    rows = []
    for target in TARGETS:
        sub = df[df["target"] == target]
        actual = sub.pivot(index="run_date", columns="horizon", values="actual").sort_index(axis=1)
        ref    = sub.pivot(index="run_date", columns="horizon", values=f"{reference}_prediction").sort_index(axis=1)
        horizons = actual.columns.to_numpy()
        n = len(actual)
        for forecaster in forecasters:
            model = sub.pivot(index="run_date", columns="horizon", values=f"{forecaster}_prediction").sort_index(axis=1)
            d = loss_differential(actual.to_numpy(), ref.to_numpy(), model.to_numpy())
            stat, p = dm_pvalue(d)
            for i, h in enumerate(horizons):
                rows.append({
                    "country": cc, "forecaster": forecaster, "target": target,
                    "horizon": int(h), "n": n,
                    "dm_stat_hac": float(stat[i]), "p_value_hac": float(p[i]),
                    "stars_hac": stars(p[i]), "hac_lags": HAC_LAGS,
                })
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reference", default="tso", metavar="NAME",
                        help="forecaster every model is tested against (default tso, the article's test)")
    args = parser.parse_args()
    suffix = "" if args.reference == "tso" else f"_vs_{args.reference}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    tables = []
    for cc in COUNTRIES:
        if not (MODELS_DIR / f"{cc}_direct.csv").exists():
            print(f"skip {cc}: no predictions (run 2_run_models.py first)")
            continue
        tables.append(evaluate_country(cc, args.reference))
    if not tables:
        return

    out = pd.concat(tables, ignore_index=True)
    path = OUT_DIR / f"dm_significance{suffix}.csv"
    out.to_csv(path, index=False, float_format="%.4f")
    print(f"saved {path}  ({len(out)} rows)")
    for thresh in (0.10, 0.05, 0.01):
        k = int((out["p_value_hac"] < thresh).sum())
        print(f"  p<{thresh:.2f}: {k}/{len(out)} cells ({100 * k / len(out):.1f}%)")


if __name__ == "__main__":
    main()
