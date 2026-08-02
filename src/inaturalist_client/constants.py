"""Constants for the iNaturalist client package.

@file constants.py
@brief Centralizes shared configuration values.
"""

from pathlib import Path

from .project_config import ProjectConfig
from .trend_region_config import TrendRegionConfig


# Project-local folder for generated cache and temporary files.
TMP_DIR = Path("tmp")

# Project-local folder for downloaded data files.
DATA_DIR = Path("data")

# Folder name for raw API page responses inside each project version.
RAW_DATA_DIR_NAME = "raw_data"

# Number of digits used in raw API page filenames.
RAW_PAGE_NUMBER_PADDING = 8

# Number of local observation IDs checked per reconciliation API request.
RECONCILE_OBSERVATION_ID_BATCH_SIZE = 25000

# Number of aggregate count rows requested per trends API page.
TREND_COUNT_PER_PAGE = 500

# Field selection used by aggregate taxon trend API requests.
TREND_TAXON_FIELDS = "(count:!t,taxon:(id:!t,name:!t,preferred_common_name:!t,rank:!t,iconic_taxon_name:!t))"

# Maximum number of IDs accepted by one iNaturalist taxa request.
TAXON_ENRICHMENT_BATCH_SIZE = 30

# Default number of observations requested by direct project-download calls.
DEFAULT_PROJECT_OBSERVATIONS_PER_PAGE = 25

# Default delay after a successful iNaturalist API request.
DEFAULT_REQUEST_COOLDOWN_SECONDS = 1.1

# Default delay before retrying a failed iNaturalist API request.
DEFAULT_FAILURE_COOLDOWN_SECONDS = 60.0

# Whether downloaded API pages are stored as JSON files by default.
DEFAULT_STORE_FILES = True

# First page number used by the iNaturalist API.
FIRST_API_PAGE_NUMBER = 1

# Value used when an API result count is absent or no results have been processed.
EMPTY_API_RESULT_COUNT = 0

# Minimum valid number of observations requested per API page.
MINIMUM_OBSERVATIONS_PER_PAGE = 0

# Minimum valid delay before requesting or retrying an API call.
MINIMUM_COOLDOWN_SECONDS = 0

# Number of result rows requested when only the API total is needed.
COUNT_REQUEST_PER_PAGE = 1

# Index of the final value returned by calendar.monthrange().
MONTHRANGE_LAST_DAY_INDEX = 1

# Initial offset used when iterating over a collection in batches.
FIRST_BATCH_OFFSET = 0

# Index of the first observation in an ordered response page.
FIRST_OBSERVATION_RESULT_INDEX = 0

# Starting depth for reconciliation's binary search.
INITIAL_RECONCILIATION_SPLIT_DEPTH = 0

# Number of IDs in a reconciliation branch that cannot be split further.
MINIMUM_RECONCILIATION_BRANCH_SIZE = 1

# Divisor used to split a reconciliation branch into two halves.
RECONCILIATION_BRANCH_DIVISOR = 2

# Increment applied when progressing through API pages or split depths.
SEQUENCE_INCREMENT = 1

# First HTTP status code in the client-error range.
FIRST_CLIENT_ERROR_STATUS_CODE = 400

# First HTTP status code in the server-error range.
FIRST_SERVER_ERROR_STATUS_CODE = 500

# HTTP status code returned when an API rate limit is exceeded.
TOO_MANY_REQUESTS_STATUS_CODE = 429

# Index of the final observation in an ordered API response page.
LAST_OBSERVATION_RESULT_INDEX = -1

# Fill character used to zero-pad page numbers in raw filenames.
RAW_PAGE_NUMBER_FILL_CHARACTER = "0"

# Project config for the OSA Biodiversity Survey.
OSA_BIODIVERSITY_SURVEY_PROJECT = ProjectConfig(alias="obs", slug="the-osa-biodiversity-survey")

# Project config for the AmistOSA Biodiversity Survey.
AMISTOSA_BIODIVERSITY_SURVEY_PROJECT = ProjectConfig(alias="abs", slug="the-amistosa-biodiversity-survey-accbd169-7488-4cbf-b8ea-caf1e31436e3")

# Projects downloaded by the default pipeline.
OSA_PROJECTS = (AMISTOSA_BIODIVERSITY_SURVEY_PROJECT, OSA_BIODIVERSITY_SURVEY_PROJECT)

# iNaturalist place ID for Costa Rica.
COSTA_RICA_PLACE_ID = 6924

# Trend region for the OSA Biodiversity Survey project.
OSA_BIODIVERSITY_SURVEY_TREND_REGION = TrendRegionConfig(
    key="obs",
    label="The OSA Biodiversity Survey",
    region_type="project",
    request_params={"project_id": OSA_BIODIVERSITY_SURVEY_PROJECT.slug},
)

# Trend region for the AmistOSA Biodiversity Survey project.
AMISTOSA_BIODIVERSITY_SURVEY_TREND_REGION = TrendRegionConfig(
    key="abs",
    label="The AmistOSA Biodiversity Survey",
    region_type="project",
    request_params={"project_id": AMISTOSA_BIODIVERSITY_SURVEY_PROJECT.slug},
)

# Trend region for all iNaturalist observations in Costa Rica.
COSTA_RICA_TREND_REGION = TrendRegionConfig(
    key="costa_rica",
    label="Costa Rica",
    region_type="place",
    request_params={"place_id": COSTA_RICA_PLACE_ID},
)

# Trend regions downloaded by the default trends pipeline.
TREND_REGIONS = (
    AMISTOSA_BIODIVERSITY_SURVEY_TREND_REGION,
    OSA_BIODIVERSITY_SURVEY_TREND_REGION,
    COSTA_RICA_TREND_REGION,
)
