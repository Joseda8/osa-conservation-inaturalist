"""Constants for the iNaturalist client package.

@file constants.py
@brief Centralizes shared configuration values.
"""

from pathlib import Path


# iNaturalist login for the OSA Conservation account.
OSA_USER_LOGIN = "osaconservation"

# Project-local folder for generated cache and temporary files.
TMP_DIR = Path("tmp")

# Project-local folder for downloaded data files.
DATA_DIR = Path("data")
