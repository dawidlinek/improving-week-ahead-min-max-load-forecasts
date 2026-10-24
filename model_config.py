"""Modeling parameters, predictor templates, and the forecast targets."""

TRAINING_WINDOW = 1092
TEST_START      = "2024-01-05"
TEST_END        = "2025-12-26"
HORIZONS        = range(3, 10)  # d+3..d+9, the TSO A31 week-ahead window
ECMWF_VARS      = ("2t", "wind_speed", "rh", "tcc", "sp", "ssr_inc")
NOON_ANCHOR     = 12            # rows are anchored at local 12:00, the issue time

# --- Column-name templates ----------------------------------------------------
POINT          = "{region}_{var}_d+{hz}"             # ECMWF point forecast (1b)
LOAD_LAG       = "load_actual_h-{h}"                 # hourly actual, h hours before noon
TSO_LEAD       = "load_forecast_h+{h}"               # hourly TSO forecast, h hours after noon
EXTREME_LAG    = "actual_daily_{key}_d-{h}"          # realised daily min/max, h days back
EXTREME        = "actual_daily_{key}_d+{hz}"         # realised daily min/max of the target day
TSO_EXTREME    = "load_forecast_daily_{key}_d+{hz}"  # TSO A31 weekly min/max forecast
TSO_TODAY      = "load_forecast_daily_{key}_d+0"     # A31 min/max forecast targeting the run day (1c)
SUN_HOLIDAY    = "is_sunday_or_holiday_d+{hz}"       # target day is a Sunday or holiday (1d)
CAPITAL_AVG    = "capital_{var}_dmean_d+{hz}"        # capital-city point, daily mean, per variable
CAPITAL_TEMP   = CAPITAL_AVG.format(var="2t", hz="{hz}")  # capital-city daily-mean temperature
CAPITAL_TP     = "capital_tp_dmean_d+{hz}"           # capital-city daily mean precipitation
CAPITAL_HDD    = "capital_hdd_d+{hz}"                # heating degree days, capital point
CAPITAL_CDD    = "capital_cdd_d+{hz}"                # cooling degree days, capital point
REGION_AVG     = "all_avg_{var}_dmean_d+{hz}"        # across-regions daily mean, per variable
REGION_TP      = "all_avg_tp_dmean_d+{hz}"           # across-regions daily mean precipitation
REGION_HDD     = "all_avg_hdd_d+{hz}"                # heating degree days, across-regions
REGION_CDD     = "all_avg_cdd_d+{hz}"                # cooling degree days, across-regions

# Degree-day bases in degrees Celsius, shared by the capital and regional
# blocks so the two are directly comparable.
HDD_BASE = 15.5
CDD_BASE = 22.0

ACTUAL_LAG_HOURS    = range(1, 169)
FORECAST_LEAD_HOURS = range(1, 36)
DAILY_LAG_DAYS      = range(1, 8)

# --- Predictors ({hz} resolved per fit) ----------------------------------------
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


REGIONAL_NWP = (BASE_PREDICTORS + [REGION_AVG.format(var=v, hz="{hz}") for v in ECMWF_VARS]
                + [REGION_TP, REGION_HDD, REGION_CDD])

# The reduced predictor set drops the two blocks whose coefficients flip sign  most between countries and weeks: the 36 hourly TSO leads and every hourly  load lag except the most recent one.
TSO_LEAD_BLOCK = [*[TSO_LEAD.format(h=h) for h in FORECAST_LEAD_HOURS], "load_forecast"]
HOURLY_LAGS_PAST_FIRST = [LOAD_LAG.format(h=h) for h in ACTUAL_LAG_HOURS if h > 1]

SCENARIOS = {
    "base":                 BASE_PREDICTORS,
    "capital_temperature":  BASE_PREDICTORS + [CAPITAL_TEMP],
    "regional_temperature": BASE_PREDICTORS + [REGION_AVG.format(var="2t", hz="{hz}")],
    "capital_nwp":          BASE_PREDICTORS + [CAPITAL_AVG.format(var=v, hz="{hz}") for v in ECMWF_VARS]
                            + [CAPITAL_TP, CAPITAL_HDD, CAPITAL_CDD],
    "regional_nwp":         REGIONAL_NWP,
    "regional_nwp_lag1_no_tso": [p for p in REGIONAL_NWP if p not in set(TSO_LEAD_BLOCK) | set(HOURLY_LAGS_PAST_FIRST)],
}

TARGETS = ("min", "max")                     

BENCH_LAG_DAYS = (1, 6)

BENCHMARKS = {
    "unbiased": {                            # TSO forecast + fitted offset (slope fixed at 1):
        "estimator":  "offset",              #   pred = tso + mean(actual - tso) over the window
        "predictors": [TSO_EXTREME],
    },
    "expert": {                             
        "estimator":  "ols",                
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


ALL_PREDICTORS = {p for t in SCENARIOS.values() for hz in HORIZONS for p in expand_horizon(t, hz)}
ALL_PREDICTORS |= {p for b in BENCHMARKS.values() for hz in HORIZONS for key in TARGETS for p in expand_target(b["predictors"], hz, key)}
