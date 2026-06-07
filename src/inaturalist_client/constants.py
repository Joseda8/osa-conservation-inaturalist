"""Constants for the iNaturalist client package.

@file constants.py
@brief Centralizes shared configuration values.
"""

from pathlib import Path

from .project_config import ProjectConfig


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
