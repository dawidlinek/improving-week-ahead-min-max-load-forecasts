"""Modeling parameters, predictor templates, and the two model readouts.

The column-name templates below are the single source for every derived
column name in the pipeline: 1d builds the columns from them and the model
scripts select them back by the same names. The "{hz}" placeholder is the
forecast horizon
"""

TRAINING_WINDOW = 1092
TEST_START      = "2024-01-05"
TEST_END        = "2025-12-26"
HORIZONS        = range(3, 10)  # d+3..d+9, the TSO A31 week-ahead window
ECMWF_VARS      = ("2t", "wind_speed", "rh", "tcc", "sp", "ssr_inc")
NOON_ANCHOR     = 12            # rows are anchored at local 12:00, the issue time

# --- Column-name templates ----------------------------------------------------
POINT        = "{region}_{var}_d+{hz}"             # ECMWF point forecast (1b)
LOAD_LAG     = "load_actual_h-{h}"                 # hourly actual, h hours before noon
TSO_LEAD     = "load_forecast_h+{h}"               # hourly TSO forecast, h hours after noon
EXTREME_LAG  = "actual_daily_{key}_d-{h}"          # realised daily min/max, h days back
EXTREME      = "actual_daily_{key}_d+{hz}"         # realised daily min/max of the target day
TSO_EXTREME  = "load_forecast_daily_{key}_d+{hz}"  # TSO A31 weekly min/max forecast
TSO_TODAY    = "load_forecast_daily_{key}_d+0"     # A31 min/max forecast targeting the run day (1c)
SUN_HOLIDAY  = "is_sunday_or_holiday_d+{hz}"       # target day is a Sunday or holiday (1d)
CURVE        = "actual_load_d+{hz}_h{key}"         # hourly-mean load of target-day hour
CAPITAL_TEMP = "capital_2t_dmean_d+{hz}"           # capital-city daily-mean temperature
REGION_AVG   = "all_avg_{var}_dmean_d+{hz}"        # across-regions daily mean, per variable
REGION_TP    = "all_avg_tp_dmean_d+{hz}"           # across-regions daily mean precipitation
REGION_HDD   = "all_avg_hdd_d+{hz}"                # heating degree days, base 18 C
REGION_CDD   = "all_avg_cdd_d+{hz}"                # cooling degree days, base 22 C

ACTUAL_LAG_HOURS    = range(1, 169)
FORECAST_LEAD_HOURS = range(1, 36)
DAILY_LAG_DAYS      = range(1, 8)

# --- Predictors (shared by both readouts; {hz} resolved per fit) ---------------
CALENDAR_CORE = [
    "is_holiday",
    *[f"is_holiday_d-{h}" for h in range(1, 8)],
    *[f"is_holiday_d+{h}" for h in range(1, 10)],
    "is_monday_d+{hz}",    "is_tuesday_d+{hz}",
    "is_wednesday_d+{hz}", "is_thursday_d+{hz}",
    "is_friday_d+{hz}",    "is_saturday_d+{hz}",
    "is_sunday_d+{hz}",
    "daylight_hours_d+{hz}",
]

LAGS_FULL = [
    *[LOAD_LAG.format(h=h) for h in ACTUAL_LAG_HOURS],
    *[TSO_LEAD.format(h=h) for h in FORECAST_LEAD_HOURS],
    "load_forecast",
]

DAILY_EXT = [
    *[EXTREME_LAG.format(key="min", h=h) for h in DAILY_LAG_DAYS],
    *[EXTREME_LAG.format(key="max", h=h) for h in DAILY_LAG_DAYS],
    *[TSO_EXTREME.format(key="min", hz=hz) for hz in HORIZONS],
    *[TSO_EXTREME.format(key="max", hz=hz) for hz in HORIZONS],
]

BASE_PREDICTORS = CALENDAR_CORE + LAGS_FULL + DAILY_EXT

SCENARIOS = {
    "base":                BASE_PREDICTORS,
    "capital_temperature": BASE_PREDICTORS + [CAPITAL_TEMP],
    "regional_nwp":        BASE_PREDICTORS + [REGION_AVG.format(var=v, hz="{hz}") for v in ECMWF_VARS]
                           + [REGION_TP, REGION_HDD, REGION_CDD],
}

READOUTS = {
    "direct": {                              # daily min/max levels
        "key":       "target",
        "keys":      ("min", "max"),
        "target":    EXTREME,
        "benchmark": TSO_EXTREME,
    },
    "profile": {                             # 24-hour load curve
        "key":       "hour",
        "keys":      tuple(range(24)),
        "target":    CURVE,
        "benchmark": None,
    },
}

# --- Benchmark models (direct readout only) ------------------------------------
# Unlike SCENARIOS, these keep the "{key}" placeholder: the design matrix is
# target-specific (only the matching min- or max-lags and TSO forecast).
# Fitted parameters are saved to models/{CC}_bench_params.csv for analysis.
BENCH_LAG_DAYS = (1, 6)

BENCHMARKS = {
    "unbiased": {                            # TSO forecast + fitted offset (slope fixed at 1):
        "estimator":  "offset",              #   pred = tso + mean(actual - tso) over the window
        "predictors": [TSO_EXTREME],
    },
    "expert": {                              # Ziel-Weron-style expert: weekday structure + TSO
        "estimator":  "ols",                 #   levels (run day + target day) + extreme lags
        "predictors": ["is_monday_d+{hz}", "is_saturday_d+{hz}", SUN_HOLIDAY,
                       TSO_TODAY, TSO_EXTREME,
                       *[EXTREME_LAG.format(key="{key}", h=h) for h in BENCH_LAG_DAYS],
                       CAPITAL_TEMP],
    },
}


def expand_horizon(templates: list[str], hz: int) -> list[str]:
    """Substitute the {hz} placeholder with the integer horizon."""
    return [t.replace("{hz}", str(hz)) for t in templates]


def expand_target(templates: list[str], hz: int, key) -> list[str]:
    """Substitute both the {hz} and {key} placeholders."""
    return [t.replace("{hz}", str(hz)).replace("{key}", str(key)) for t in templates]


# Every predictor any scenario or benchmark references at any horizon. 1d keeps
# only these out of the ~2000 raw columns; everything else it builds itself.
ALL_PREDICTORS = {p for t in SCENARIOS.values() for hz in HORIZONS for p in expand_horizon(t, hz)}
ALL_PREDICTORS |= {p for b in BENCHMARKS.values() for hz in HORIZONS
                   for key in READOUTS["direct"]["keys"] for p in expand_target(b["predictors"], hz, key)}
