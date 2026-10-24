"""
Download TSO load from ENTSO-E and join with the extracted ECMWF point data into a single 15-min CSV per country.

Requires the ENTSOE_API_KEY environment variable and epftoolbox2 2.3 or newer.

Produces per country (under data/raw/raw_{CC}.csv) the columns consumed by
1d_prepare_features.py:
  - load_actual, load_forecast
  - is_monday_d+0..d+9, ..., is_sunday_d+0..d+9    (weekday one-hot)
  - daylight_hours_d+0..d+9                        (daylight at the capital)
  - is_holiday_d-9..d+9                            (holiday flags, lags and leads)
  - load_forecast_daily_min_d+0..d+9,
    load_forecast_daily_max_d+0..d+9               (TSO A31 daily min/max leads)
  - {city}_{var}_d+3 .. {city}_{var}_d+9           (ECMWF point forecasts from 1b)

Usage: python 1c_download_load.py [--countries PT DE ...]
"""

import argparse
import os
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
from epftoolbox2.pipelines import DataPipeline
from epftoolbox2.data.sources import EntsoeSource, CalendarSource, CsvSource
from epftoolbox2.data.transformers import Transformer, ResampleTransformer, LagTransformer, TimezoneTransformer, LambdaTransformer
from epftoolbox2.data.validators import CoverageValidator, DSTStructureValidator

from country_config import COUNTRIES, capital_latlon

ROOT             = Path(__file__).parent
ECMWF_POINTS_DIR = ROOT / "data" / "ecmwf_points"
OUTPUT_DIR       = ROOT / "data" / "raw"

START   = pd.Timestamp("2021-01-01", tz="UTC")
END     = pd.Timestamp("2026-02-01", tz="UTC")   # kept as the last row
RUN_END = END + pd.Timedelta("1s")               # run() is [start, end)

DAILY       = ["load_forecast_daily_min", "load_forecast_daily_max"]
STEP_FILLED = ["load_actual", "load_forecast", *DAILY]
LEAD_COLS   = ["is_monday", "is_tuesday", "is_wednesday", "is_thursday", "is_friday", "is_saturday", "is_sunday", "daylight_hours", *DAILY, "is_holiday"]
DAY_LAG     = re.compile(r"_h([+-])(\d+)$")


class ClipRange(Transformer):
    """Keep [START, END] and leave the A31 columns empty before the first local midnight, as the published raw frames have them."""

    def __init__(self, start: pd.Timestamp, end: pd.Timestamp):
        self.start, self.end = start, end

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.loc[self.start:self.end].copy()
        df.loc[df.index < self.start.tz_convert(df.index.tz).ceil("D"), DAILY] = np.nan
        return df


def build_pipeline(code: str, info: dict) -> DataPipeline:
    tz = info["tz"]
    cap_lat, cap_lon = capital_latlon(info)

    pipeline = DataPipeline(timezone=tz, on_invalid="warn")
    pipeline.add_source(EntsoeSource(country_code=code, api_key=os.environ["ENTSOE_API_KEY"], type=["load"], prefer_15min=True))
    pipeline.add_source(CsvSource(str(ECMWF_POINTS_DIR / f"{info['name']}_ecmwf_points.csv"), datetime_column="timestamp", timezone="UTC"))
    pipeline.add_source(CalendarSource(country=info["calendar"], timezone=tz, holidays="binary", weekday="onehot", daylight=True, lat=cap_lat, lon=cap_lon, freq="1h"))
    pipeline.add_transformer(TimezoneTransformer(target_tz=tz, daily_columns=DAILY, daily_anchor=None))
    pipeline.add_transformer(ResampleTransformer(freq="15min", agg="first", fill={"default": None, **{c: "ffill" for c in STEP_FILLED}}))
    pipeline.add_transformer(LambdaTransformer(func=lambda df: df.assign(**{c: df[c].ffill() for c in STEP_FILLED}).round(3)))
    pipeline.add_transformer(ClipRange(START, END))
    pipeline.add_transformer(LagTransformer(lags=range(-9, 0), freq="24h", columns=LEAD_COLS))
    pipeline.add_transformer(LagTransformer(lags=range(1, 10), freq="24h", columns=["is_holiday"]))
    pipeline.add_validator(CoverageValidator(columns=["load_actual"], freq="15min", min_coverage=1.0))
    pipeline.add_validator(DSTStructureValidator(freq="15min", allow_partial_edges=True))
    return pipeline


def day_lag_names(df: pd.DataFrame) -> pd.DataFrame:
    """x_h+216 -> x_d+9, x_h-24 -> x_d-1, plus the x_d+0 copies of the lead columns."""
    df = df.rename(columns=lambda c: DAY_LAG.sub(lambda m: f"_d{m[1]}{int(m[2]) // 24}", c))
    return df.assign(**{f"{c}_d+0": df[c] for c in LEAD_COLS})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--countries", nargs="*", metavar="CC", default=list(COUNTRIES))
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for code in args.countries:
        info = COUNTRIES[code]
        print(f"\n=== {code} ===")
        pipeline = build_pipeline(code, info)
        df = None
        for attempt in range(1, 6):
            try:
                df = pipeline.run(start=START, end=RUN_END, cache=True)
                break
            except Exception as e:
                print(f"attempt {attempt}/5 failed for {code}: {e}")
                time.sleep(30)
        if df is None:
            print(f"giving up on {code} after 5 attempts")
            continue
        df = day_lag_names(df)
        out = OUTPUT_DIR / f"raw_{code}.csv"
        df.to_csv(out)
        print(f"saved {out}  ({len(df):,} rows, {len(df.columns):,} cols)")


if __name__ == "__main__":
    main()
