"""
Extract ECMWF TIGGE forecast data at city locations from monthly GRIB files.

Reads GRIB with earthkit-data: fields are filtered per variable with
FieldList.sel, decoded in bulk with to_numpy, and the city grid points are
sliced out of the native reduced Gaussian grid by nearest-neighbour argmin.

For each init day (00:00 UTC) emits 4 rows at timestamps 00/06/12/18 UTC.
Columns: {region}_{var}_d+3 ... {region}_{var}_d+9 (the HORIZONS window)

Variables stored per city (GRIB shortNames used as column labels):
  Raw GRIB: 2t, 2d, mx2t6, mn2t6, 10u, 10v, ssr, tp, tcc, sp
            (mx2t6/mn2t6 are the 2-m temperature extremes over the 6 h ending at each step)
  Derived:  wind_speed = sqrt(10u^2 + 10v^2)
            rh         = relative humidity % (Magnus formula from 2t + 2d)
            ssr_inc    = 6-hourly solar radiation increment (ssr[step] - ssr[step-6h])
            tp_inc     = 6-hourly precipitation increment (same differencing)

Output: data/ecmwf_points/{country}_ecmwf_points.csv
"""

import glob
from pathlib import Path

import earthkit.data as ekd
import numpy as np
import pandas as pd

from country_config import COUNTRIES
from model_config import HORIZONS, POINT

CITIES_BY_COUNTRY = {info["name"]: info["regions"] for info in COUNTRIES.values()}

RAW_GRIB_VARS = ("2t", "2d", "mx2t6", "mn2t6", "10u", "10v", "ssr", "tp", "tcc", "sp")

SUB_DAY_HOURS = [0, 6, 12, 18]

ROOT       = Path(__file__).parent
GRIB_DIR   = ROOT / "data" / "ecmwf_grib"
OUTPUT_DIR = ROOT / "data" / "ecmwf_points"


def rh_magnus(t_k: np.ndarray, td_k: np.ndarray) -> np.ndarray:
    """Relative humidity (%) from temperature and dewpoint in Kelvin."""
    t_c  = t_k  - 273.15
    td_c = td_k - 273.15
    a, b = 17.625, 243.04
    return 100.0 * np.exp(a * td_c / (b + td_c)) / np.exp(a * t_c / (b + t_c))


def make_increments(arr: np.ndarray, steps_h: np.ndarray) -> np.ndarray:
    """Convert accumulated field to 6-hourly increments (step value − step-6h value)."""
    s_pos = {h: i for i, h in enumerate(steps_h)}
    inc = arr.copy()
    for s_i, lead_h in enumerate(steps_h):
        if (prev := s_pos.get(lead_h - 6)) is not None:
            inc[:, s_i, :] = arr[:, s_i, :] - arr[:, prev, :]
    return inc


def _build_wide_df(vars_3d: dict, init_times: pd.DatetimeIndex, steps_h: np.ndarray, codes: list) -> pd.DataFrame:
    """(init, step, city) cubes → wide DataFrame, one row per (init_time + H hours)."""
    s_pos = {h: i for i, h in enumerate(steps_h)}
    frames = []
    for H in SUB_DAY_HOURS:
        cols = {
            POINT.format(region=code, var=label, hz=d): arr[:, s_i, ci]
            for d in HORIZONS if (s_i := s_pos.get(H + 24 * d)) is not None
            for label, arr in vars_3d.items()
            for ci, code in enumerate(codes)
        }
        if cols:
            frames.append(pd.DataFrame(cols, index=init_times + pd.Timedelta(hours=H)))
    return pd.concat(frames) if frames else pd.DataFrame()


def extract_grib(grib_path: str, cities_by_country: dict) -> dict:
    """Returns {country: DataFrame with rows=timestamps, cols={city}_{var}_d+{h}}."""
    fieldlist = ekd.from_source("file", grib_path).to_fieldlist()
    if len(fieldlist) == 0:
        print("    no GRIB messages found")
        return {c: pd.DataFrame() for c in cities_by_country}

    geo = fieldlist[0].geography
    lats, lons = geo.latitudes(), geo.longitudes()
    lons = np.where(lons > 180, lons - 360, lons)
    cities = [(country, code, c) for country, regs in cities_by_country.items() for code, c in regs.items()]
    city_idx = np.array([np.argmin((lats - c["lat"])**2 + (lons - c["lon"])**2) for *_, c in cities])

    # Per variable: filter with sel, decode all fields at once, keep only city columns.
    raw = {}
    for var in RAW_GRIB_VARS:
        sub = fieldlist.sel({"parameter.variable": var})
        if len(sub) == 0:
            print(f"    [{var:4s}] not in file, skipped")
            continue
        vals = sub.to_numpy(flatten=True)
        assert vals.shape[1] == lats.size, f"{var}: grid changed mid-file"
        raw[var] = (np.array(sub.metadata("date")), np.array(sub.metadata("step"), dtype=int), vals[:, city_idx].astype(np.float32))
    if not raw:
        return {c: pd.DataFrame() for c in cities_by_country}

    # (init, step, city) cube per variable; combos a variable lacks stay NaN.
    init_dates = np.unique(np.concatenate([d for d, _, _ in raw.values()]))
    steps_h    = np.unique(np.concatenate([s for _, s, _ in raw.values()]))
    cubes = {}
    for var, (dates, steps, vals) in raw.items():
        arr = np.full((init_dates.size, steps_h.size, len(cities)), np.nan, dtype=np.float32)
        arr[np.searchsorted(init_dates, dates), np.searchsorted(steps_h, steps)] = vals
        cubes[var] = arr
    cubes["wind_speed"] = np.sqrt(cubes["10u"]**2 + cubes["10v"]**2)
    cubes["rh"]         = rh_magnus(cubes["2t"], cubes["2d"])
    cubes["ssr_inc"]    = make_increments(cubes["ssr"], steps_h)
    cubes["tp_inc"]     = make_increments(cubes["tp"], steps_h)

    init_times = pd.DatetimeIndex([pd.Timestamp(str(d)) for d in init_dates])
    out = {}
    for country in cities_by_country:
        idx   = [i for i, (ctry, *_) in enumerate(cities) if ctry == country]
        codes = [code for ctry, code, _ in cities if ctry == country]
        out[country] = _build_wide_df({v: a[:, :, idx] for v, a in cubes.items()}, init_times, steps_h, codes)
    return out


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    grib_files = sorted(glob.glob(str(GRIB_DIR / "*.grib")))
    if not grib_files:
        print(f"No GRIB files in {GRIB_DIR}")
        return

    monthly: dict[str, list[pd.DataFrame]] = {c: [] for c in CITIES_BY_COUNTRY}
    for i, grib_path in enumerate(grib_files, 1):
        print(f"\n[{i}/{len(grib_files)}] {grib_path}")
        for country, df in extract_grib(grib_path, CITIES_BY_COUNTRY).items():
            if not df.empty:
                monthly[country].append(df)

    for country, dfs in monthly.items():
        if not dfs:
            print(f"\n{country}: no data extracted")
            continue
        df = pd.concat(dfs).sort_index()
        df.index.name = "timestamp"
        df = df.reindex(sorted(df.columns), axis=1)
        out_path = OUTPUT_DIR / f"{country}_ecmwf_points.csv"
        df.to_csv(out_path, float_format="%.3f")
        print(f"{country}: {len(df):,} rows x {len(df.columns):,} cols -> {out_path}")


if __name__ == "__main__":
    main()
