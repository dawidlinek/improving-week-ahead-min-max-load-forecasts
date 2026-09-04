"""
Download ECMWF TIGGE high-resolution forecasts from the CDS API.

One GRIB file per month covering Europe. Each file holds the 00:00 UTC init
forecast with 6-hourly leadtimes covering the d+3..d+9 target window (66-234 h).

Requires the CDS_API_KEY environment variable. See https://cds.climate.copernicus.eu/

Output: data/ecmwf_grib/{YYYY}_{MM}.grib
"""

import calendar
import os
from pathlib import Path

import cdsapi

from model_config import HORIZONS

DATASET = "tigge-forecasts"

VARIABLES = [
    "2_m_temperature",
    "2_m_dewpoint_temperature",
    "10_m_u_component_of_wind",
    "10_m_v_component_of_wind",
    "surface_net_solar_radiation",
    "total_cloud_cover",
    "surface_pressure",
    "total_precipitation",
    "maximum_2_m_temperature_in_the_last_6_hours",
    "minimum_2_m_temperature_in_the_last_6_hours",
]

# 6-hourly leadtimes covering 00/06/12/18 UTC of days d+3..d+9, plus one step
# before the first so accumulated fields (ssr, tp) can be differenced in 1b.
FIRST_LEAD = 24 * min(HORIZONS) - 6
LAST_LEAD  = 24 * max(HORIZONS) + 18
LEADTIME_HOURS = [str(h) for h in range(FIRST_LEAD, LAST_LEAD + 1, 6)]

START_YEAR, START_MONTH = 2021, 1
END_YEAR,   END_MONTH   = 2026, 6

# N, W, S, E — Europe bounding box.
AREA = [75, -15, 30, 37]

OUTPUT_DIR = Path(__file__).parent / "data" / "ecmwf_grib"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    client = cdsapi.Client(
        url="https://ecds.ecmwf.int/api",
        key=os.environ["CDS_API_KEY"],
    )

    for year in range(START_YEAR, END_YEAR + 1):
        month_start = START_MONTH if year == START_YEAR else 1
        month_end   = END_MONTH   if year == END_YEAR   else 12

        for month in range(month_start, month_end + 1):
            out = OUTPUT_DIR / f"{year}_{month:02d}.grib"
            if out.exists():
                print(f"skip  {year}-{month:02d}  (already exists)")
                continue

            days = [f"{d:02d}" for d in range(1, calendar.monthrange(year, month)[1] + 1)]
            print(f"fetch {year}-{month:02d} ...")
            client.retrieve(DATASET, {
                "origin":           "ecmwf",
                "year":             str(year),
                "month":            f"{month:02d}",
                "day":              days,
                "time":             "00:00",
                "level_type":       "single_level",
                "variable":         VARIABLES,
                "forecast_type":    "high_resolution_forecast",
                "leadtime_hour":    LEADTIME_HOURS,
                "data_format":      "grib",
                "area":             AREA,
            }).download(str(out))
            print(f"saved {out}")


if __name__ == "__main__":
    main()
