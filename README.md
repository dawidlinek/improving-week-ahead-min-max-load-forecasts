# improving-week-ahead-min-max-load-forecasts

Research code for improving week-ahead forecasts of daily minimum and maximum electricity load
across 20 European markets.

Transmission system operators publish their own week-ahead minimum and maximum load forecast as
the ENTSO-E A31 series, issued every Friday for the following Monday to Sunday, which covers
horizons of three to nine days ahead. This repository fits rolling-window LASSO models on
calendar, load-lag, TSO-forecast and ECMWF weather features and scores them against that
operational TSO benchmark.

## Requirements

Python 3.10 or newer. The interpreter is pinned in `.python-version`, the dependency list is in
`pyproject.toml` and the exact versions used are in `uv.lock`.

```bash
uv sync
```

Then either activate `.venv` or prefix each command below with `uv run`. Without uv,
`pip install -e .` installs the same dependency list, unpinned.

The GRIB reader in step 1b needs the ecCodes library. On Linux and macOS it is installed
automatically as `eccodeslib`. That package publishes no Windows wheels, so on Windows install
ecCodes from conda-forge first, or run step 1b under WSL. Steps 1c to 4 do not need it.

```bash
conda install -c conda-forge eccodes
```

Two API keys are read from the environment by the download steps. No key is stored in this
repository.

| Variable | Used by | Source |
|---|---|---|
| `CDS_API_KEY` | `1a_download_ecmf.py` | Copernicus Climate Data Store |
| `ENTSOE_API_KEY` | `1c_download_load.py` | ENTSO-E Transparency Platform |

## Pipeline

Run from the repository root, in order.

```bash
python 1a_download_ecmf.py     # ECMWF TIGGE via the CDS API   -> data/ecmwf_grib/
python 1b_extract_ecmf.py      # GRIB to per-region point CSVs -> data/ecmwf_points/
python 1c_download_load.py     # ENTSO-E load and A31 forecast -> data/raw/
python 1d_prepare_features.py  # 15-min raw to daily features  -> data/features/
python 2_run_models.py         # rolling-window LassoCV        -> models/
python 3_evaluate_extremes.py  # score every forecaster        -> results/extremes_errors.csv
python 4_dm_test.py            # Diebold-Mariano vs the TSO    -> results/dm_significance.csv
```

Steps 1a to 1c are long running and hit rate-limited external APIs. Steps 1d to 4 run offline
from whatever those produced.

Step 2 accepts optional arguments.

```bash
python 2_run_models.py --readout direct    # or profile, or both
python 2_run_models.py --countries PT DE
```

## What is being fitted

Two readouts share one feature set, one training window and one leakage guard, and differ only
in the target column.

| Readout | Target |
|---|---|
| `direct` | the realized daily minimum and maximum, directly comparable to the TSO forecast |
| `profile` | the full 24-hour load curve, from which minimum and maximum are then derived |

Three weather scenarios extend the same base predictor set.

| Scenario | Adds |
|---|---|
| `base` | nothing, so calendar terms, load lags and the TSO forecast alone |
| `capital_temperature` | capital-city daily mean temperature |
| `regional_nwp` | six ECMWF variables and precipitation averaged across a country's regions, plus derived HDD and CDD, for nine weather regressors |

Two reference benchmarks are fitted alongside them, direct readout only.

| Benchmark | Form |
|---|---|
| `unbiased` | the TSO forecast plus a fitted offset, with the slope held at one |
| `expert` | weekday structure, TSO levels for the run day and the target day, two extreme lags and capital temperature, by OLS |

One `LassoCV` is fitted per (country, scenario, week, horizon, readout).

| Setting | Value |
|---|---|
| Training window | 1092 days, rolling |
| Test window | 2024-01-05 to 2025-12-26 |
| Horizons | d+3 to d+9 |
| Markets | 20 |
| Row anchor | local 12:00, the assumed Friday issue time |

## Configuration

`model_config.py` holds every modeling parameter and the column-name templates. Those templates
are the single source for every derived column name in the pipeline. Step 1d builds the columns
from them and every later script selects the columns back by the same templates, so a rename in
one place propagates through the whole pipeline.

`country_config.py` holds the 20 markets and one latitude and longitude weather-sampling point
per administrative region. Every script imports it, so region counts cannot drift apart between
the sampling map and the tables.