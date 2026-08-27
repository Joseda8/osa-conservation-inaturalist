"""Pipeline configuration constants.

@file constants.py
@brief Defines defaults used by the command-line pipeline interface.
"""

from pathlib import Path


# Pipeline steps run when the --steps argument is omitted.
DEFAULT_PIPELINE_STEP_NAMES = ("download-raw-data", "migrate-db", "load-raw-data-to-db")

# Default value before --steps is resolved to the default pipeline steps.
DEFAULT_SELECTED_PIPELINE_STEPS = None

# Default named pipeline when --pipeline is omitted.
DEFAULT_NAMED_PIPELINE = None

# Default year for a named pipeline when no year is supplied.
DEFAULT_PIPELINE_YEAR = None

# Default month for a named pipeline when no month is supplied.
DEFAULT_PIPELINE_MONTH = None

# Name of the pipeline that refreshes one complete calendar month.
MONTHLY_UPDATE_PIPELINE_NAME = "monthly-update"

# Name of the pipeline that imports all available historical data.
HISTORICAL_LOAD_PIPELINE_NAME = "historical-load"

# Name of the pipeline that authorizes the local Google user without uploading reports.
GOOGLE_AUTH_PIPELINE_NAME = "auth-with-google"

# Step run by the Google authorization pipeline.
GOOGLE_AUTH_PIPELINE_STEP_NAMES = ("auth-with-google",)

# Steps that download, load, reconcile, and enrich a data update.
DATA_UPDATE_PIPELINE_STEP_NAMES = ("download-raw-data", "download-trends", "load-raw-data-to-db", "reconcile-project-observations", "enrich-taxonomy")

# CSV reports generated from the ABS and OBS observation data.
ABS_VS_OBS_REPORTS = (
    ("abs-vs-obs-observation-counts.csv", Path("db") / "queries" / "dashboard" / "abs_vs_obs_observation_counts.sql"),
    ("abs-vs-obs-observations-by-day.csv", Path("db") / "queries" / "dashboard" / "abs_vs_obs_observations_by_day.sql"),
    ("abs-vs-obs-duplicate-observations.csv", Path("db") / "queries" / "dashboard" / "abs_vs_obs_duplicate_observations.sql"),
    ("abs-vs-obs-quality-grades.csv", Path("db") / "queries" / "dashboard" / "abs_vs_obs_quality_grades.sql"),
)

# Root folder for locally generated dashboard CSV reports.
PROCESSED_DATA_DIRECTORY = Path("data") / "processed-data"

# Date format used for dated local dashboard report folders.
PROCESSED_DATA_DATE_FORMAT = "%Y%m%d"

# Folder containing generated CSV reports consumed by the GitHub Pages React build.
GITHUB_PAGES_DATA_DIRECTORY = Path("web") / "public" / "data"

# Whether the command-line interface lists steps instead of running the pipeline.
DEFAULT_LIST_STEPS = False

# Number of observations requested in each iNaturalist API page.
DEFAULT_OBSERVATIONS_PER_PAGE = 100

# Seconds to wait after a successful iNaturalist API request.
DEFAULT_REQUEST_COOLDOWN_SECONDS = 1.1

# Seconds to wait after a failed iNaturalist API request before retrying.
DEFAULT_FAILURE_COOLDOWN_SECONDS = 60.0

# Download mode used when no explicit mode is supplied.
DEFAULT_DOWNLOAD_MODE = "incremental"

# Optional incremental-download cutoff when no explicit value is supplied.
DEFAULT_UPDATED_SINCE = None

# Optional first observed date for a bounded observation download.
DEFAULT_OBSERVED_DATE_START = None

# Optional final observed date for a bounded observation download.
DEFAULT_OBSERVED_DATE_END = None

# Optional raw-data snapshot date when no explicit value is supplied.
DEFAULT_LOAD_DATE = None

# Optional first year of trend data when no explicit value is supplied.
DEFAULT_TREND_YEAR = None

# Optional first month of trend data when no explicit value is supplied.
DEFAULT_TREND_MONTH = None

# Optional final year of a bounded monthly trend download.
DEFAULT_TREND_END_YEAR = None

# Optional final month of a bounded monthly trend download.
DEFAULT_TREND_END_MONTH = None

# Trend download mode used when no explicit mode is supplied.
DEFAULT_TREND_MODE = "since"

# Taxonomy enrichment mode used when no explicit mode is supplied.
DEFAULT_TAXONOMY_MODE = "missing"
