"""Pipeline configuration constants.

@file constants.py
@brief Defines defaults used by the command-line pipeline interface.
"""


# Pipeline steps run when the --steps argument is omitted.
DEFAULT_PIPELINE_STEP_NAMES = ("download-raw-data", "migrate-db", "load-raw-data-to-db")

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

# Optional raw-data snapshot date when no explicit value is supplied.
DEFAULT_LOAD_DATE = None

# Optional first year of trend data when no explicit value is supplied.
DEFAULT_TREND_YEAR = None

# Optional first month of trend data when no explicit value is supplied.
DEFAULT_TREND_MONTH = None

# Trend download mode used when no explicit mode is supplied.
DEFAULT_TREND_MODE = "since"

# Taxonomy enrichment mode used when no explicit mode is supplied.
DEFAULT_TAXONOMY_MODE = "missing"
