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

# Project config for the OSA Biodiversity Survey.
OSA_BIODIVERSITY_SURVEY_PROJECT = ProjectConfig(
    alias="obs",
    slug="the-osa-biodiversity-survey",
)

# Project config for the AmistOSA Biodiversity Survey.
AMISTOSA_BIODIVERSITY_SURVEY_PROJECT = ProjectConfig(
    alias="abs",
    slug="the-amistosa-biodiversity-survey-accbd169-7488-4cbf-b8ea-caf1e31436e3",
)

# Projects downloaded by the default pipeline.
OSA_PROJECTS = (
    OSA_BIODIVERSITY_SURVEY_PROJECT,
    AMISTOSA_BIODIVERSITY_SURVEY_PROJECT,
)

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
    OSA_BIODIVERSITY_SURVEY_TREND_REGION,
    AMISTOSA_BIODIVERSITY_SURVEY_TREND_REGION,
    COSTA_RICA_TREND_REGION,
)
