"""
Download TSO load (actual + day-ahead forecast) from ENTSO-E and join with the extracted ECMWF point data into a single 15-min CSV per country.

Requires the ENTSOE_API_KEY environment variable.

Produces per country (under data/raw/raw_{CC}.csv) the columns consumed by
1d_prepare_features.py:
  - load_actual, load_forecast                     (15-min)
  - is_monday_d+0..d+9, ..., is_sunday_d+0..d+9    (weekday one-hot, daily leads)
  - daylight_hours_d+0..d+9                        (daylight at the capital)
  - is_holiday_d-9..d+9                            (holiday flags, lags and leads)
  - load_forecast_daily_min_d+0..d+9,
    load_forecast_daily_max_d+0..d+9               (TSO A31 daily min/max leads;
    d+0 is the A31 value whose target date is the row's own day)
  - {city}_{var}_d+3 .. {city}_{var}_d+9           (ECMWF point forecasts from 1b)

Hourly lag features for load_actual and load_forecast are computed in
1d_prepare_features.py from hourly means, not here — that way they're true
hourly averages rather than 15-min snapshots taken at hourly offsets.
"""

import os
import time
from pathlib import Path

from epftoolbox2.pipelines import DataPipeline
from epftoolbox2.data.sources import EntsoeSource, CalendarSource, CsvSource
from epftoolbox2.data.transformers import (ResampleTransformer, LagTransformer, TimezoneTransformer,)
from epftoolbox2.data.validators import NullCheckValidator, ContinuityValidator

from country_config import COUNTRIES, capital_latlon

ROOT             = Path(__file__).parent
ECMWF_POINTS_DIR = ROOT / "data" / "ecmwf_points"
OUTPUT_DIR       = ROOT / "data" / "raw"

START = "2021-01-01"
END   = "2026-02-01"


def build_pipeline(code: str, info: dict) -> DataPipeline:
    # Capital coords pin daylight hours to the same point the rest of the pipeline is geo-referenced to.
    cap_lat, cap_lon = capital_latlon(info)

    pipeline = DataPipeline()
    pipeline.add_source(EntsoeSource(country_code=code, api_key=os.environ["ENTSOE_API_KEY"], type=["load"], prefer_15min=True))
    pipeline.add_source(CsvSource(str(ECMWF_POINTS_DIR / f"{info['name']}_ecmwf_points.csv"), datetime_column="timestamp"))
    pipeline.add_source(CalendarSource(country=info["calendar"], holidays="binary", weekday="onehot", daylight=True, lat=cap_lat, lon=cap_lon))
    pipeline.add_transformer(TimezoneTransformer(target_tz=info["tz"]))
    pipeline.add_transformer(ResampleTransformer(freq="15min", columns=["load_actual", "load_forecast", "load_forecast_daily_min", "load_forecast_daily_max"], method="ffill"))
    pipeline.add_transformer(LagTransformer(lags=range(-9, 1), freq="day", columns=[ "is_monday", "is_tuesday", "is_wednesday", "is_thursday", "is_friday", "is_saturday", "is_sunday", "daylight_hours", "load_forecast_daily_min", "load_forecast_daily_max", "is_holiday"]))
    pipeline.add_transformer(LagTransformer(lags=range(1, 10), freq="day", columns=["is_holiday"]))
    pipeline.add_validator(NullCheckValidator(columns=["load_actual"]))
    pipeline.add_validator(ContinuityValidator())
    return pipeline


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for code, info in COUNTRIES.items():
        print(f"\n=== {code} ===")
        pipeline = build_pipeline(code, info)
        df = None
        for attempt in range(1, 6):  # ENTSO-E API is flaky; retry with a pause
            try:
                df = pipeline.run(start=START, end=END, cache=True)
                break
            except Exception as e:
                print(f"attempt {attempt}/5 failed for {code}: {e}")
                time.sleep(30)
        if df is None:
            print(f"giving up on {code} after 5 attempts")
            continue
        df = df.rename(columns={c: c.replace("_d-0", "_d+0") for c in df.columns if c.endswith("_d-0")})
        out = OUTPUT_DIR / f"raw_{code}.csv"
        df.to_csv(out)
        print(f"saved {out}  ({len(df):,} rows, {len(df.columns):,} cols)")


if __name__ == "__main__":
    main()
