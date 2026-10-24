"""Reduce each 15-min raw CSV into one daily feature frame per country.

Reads:  data/raw/raw_{CC}.csv        (15-min -- output of 1c)
Writes: data/features/data_{CC}.csv  (one row per day -- consumed by 2)

Each row is anchored at local 12:00, the assumed Friday-noon issue time, so
every lag column reflects what is known at that hour.
"""

import argparse
from pathlib import Path

import pandas as pd

from country_config import COUNTRIES, capital_code
from model_config import (ECMWF_VARS, NOON_ANCHOR, HORIZONS,
                          POINT, LOAD_LAG, TSO_LEAD, EXTREME_LAG, EXTREME,
                          CAPITAL_AVG, CAPITAL_TP, CAPITAL_HDD, CAPITAL_CDD,
                          REGION_AVG, REGION_TP, REGION_HDD, REGION_CDD,
                          HDD_BASE, CDD_BASE, SUN_HOLIDAY,
                          ACTUAL_LAG_HOURS, FORECAST_LEAD_HOURS, DAILY_LAG_DAYS,
                          ALL_PREDICTORS)

ROOT       = Path(__file__).parent
INPUT_DIR  = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data" / "features"


FAMILIES = {                
    "capital": (CAPITAL_AVG, CAPITAL_TP, CAPITAL_HDD, CAPITAL_CDD),
    "region":  (REGION_AVG,  REGION_TP,  REGION_HDD,  REGION_CDD),
}


def weather_features(df: pd.DataFrame, country: str) -> dict[str, pd.Series]:
    codes = {"capital": [capital_code(COUNTRIES[country])],
             "region":  list(COUNTRIES[country]["regions"])}

    def daily_mean(cols: list[str]) -> pd.Series | None:
        cols = [c for c in cols if c in df.columns]
        return df[cols].mean(axis=1).resample("1D").mean() if cols else None

    weather: dict[str, pd.Series] = {}
    for hz in HORIZONS:
        for family, (avg_t, tp_t, hdd_t, cdd_t) in FAMILIES.items():
            for v in ECMWF_VARS:
                series = daily_mean([POINT.format(region=c, var=v, hz=hz) for c in codes[family]])
                if series is not None:
                    weather[avg_t.format(var=v, hz=hz)] = series

            mean_2t = weather.get(avg_t.format(var="2t", hz=hz))
            if mean_2t is not None:
                t_c = mean_2t - 273.15
                weather[hdd_t.format(hz=hz)] = (HDD_BASE - t_c).clip(lower=0)
                weather[cdd_t.format(hz=hz)] = (t_c - CDD_BASE).clip(lower=0)
            tp = daily_mean([POINT.format(region=c, var="tp_inc", hz=hz) for c in codes[family]])
            if tp is not None:
                weather[tp_t.format(hz=hz)] = tp
    return weather


def build_features(country: str, tz: str, csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(tz)

    daylight_cols = [c for c in df.columns if c.startswith("daylight_hours")]
    df[daylight_cols] = df[daylight_cols].interpolate("time").ffill().bfill()

    # Daily extremes from 15-min load (the TSO's operational measurement);
    # hourly means for lags.
    daily = {"min": df["load_actual"].resample("1D").min(), "max": df["load_actual"].resample("1D").max()}
    hourly_actual   = df["load_actual"].resample("1h").mean()
    hourly_forecast = df["load_forecast"].resample("1h").mean()

    weather = weather_features(df, country)

    noon_rows = df[df.index.hour == NOON_ANCHOR].resample("1D").first()
    predictors = noon_rows[[c for c in noon_rows.columns if c in ALL_PREDICTORS]]
    run_days = noon_rows.index.tz_localize(None).normalize()
    noon = (run_days + pd.Timedelta(hours=NOON_ANCHOR)).tz_localize(tz)

    extra = {
        **{LOAD_LAG.format(h=h): hourly_actual.reindex(noon - pd.Timedelta(hours=h)).values for h in ACTUAL_LAG_HOURS},
        **{TSO_LEAD.format(h=h): hourly_forecast.reindex(noon + pd.Timedelta(hours=h)).values for h in FORECAST_LEAD_HOURS},
        **{EXTREME_LAG.format(key=k, h=h): daily[k].shift(h) for k in daily for h in DAILY_LAG_DAYS},
        **{EXTREME.format(key=k, hz=hz): daily[k].shift(-hz) for k in daily for hz in HORIZONS},
        # Sunday-or-holiday folds the two low-load day types into one dummy for the expert benchmark.
        **{SUN_HOLIDAY.format(hz=hz): noon_rows[[f"is_sunday_d+{hz}", f"is_holiday_d+{hz}"]].max(axis=1) for hz in HORIZONS},
        **weather,
        "day": (run_days - run_days[0]).days,
    }
    return pd.concat([predictors, pd.DataFrame(extra, index=noon_rows.index)], axis=1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--countries", nargs="*", metavar="CC", default=list(COUNTRIES))
    parser.add_argument("--force", action="store_true", help="rebuild frames that already exist")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for cc in args.countries:
        info     = COUNTRIES[cc]
        in_path  = INPUT_DIR  / f"raw_{cc}.csv"
        out_path = OUTPUT_DIR / f"data_{cc}.csv"
        if not in_path.exists():
            print(f"skip {cc}: {in_path} not found (run 1c_download_load.py first)")
            continue
        if out_path.exists() and not args.force:
            print(f"skip {cc}: {out_path} already exists (--force to rebuild)")
            continue

        print(f"--- {cc} --- loading {in_path.name}")
        features = build_features(cc, info["tz"], in_path)
        features.to_csv(out_path)
        print(f"saved {out_path}  ({len(features):,} rows x {len(features.columns):,} cols)")


if __name__ == "__main__":
    main()
