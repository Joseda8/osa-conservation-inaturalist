"""Google Drive integration constants.

@file constants.py
@brief Defines Google Drive upload configuration values.
"""

from pathlib import Path


# Required environment variable containing the destination Google Drive folder ID.
GOOGLE_DRIVE_UPLOAD_FOLDER_ID_ENV_VAR = "GOOGLE_DRIVE_UPLOAD_FOLDER_ID"

# Environment variable containing the complete Google service account JSON.
GOOGLE_SERVICE_ACCOUNT_JSON_ENV_VAR = "GOOGLE_SERVICE_ACCOUNT_JSON"

# Optional environment variable overriding the local service account JSON path.
GOOGLE_SERVICE_ACCOUNT_JSON_PATH_ENV_VAR = "GOOGLE_SERVICE_ACCOUNT_JSON_PATH"

# Default ignored local path containing Google service account credentials.
DEFAULT_GOOGLE_SERVICE_ACCOUNT_JSON_PATH = Path(".secrets") / "google-service-account.json"

# Optional environment variable overriding the uploaded observations CSV filename.
GOOGLE_DRIVE_OBSERVATIONS_CSV_FILE_NAME_ENV_VAR = "GOOGLE_DRIVE_OBSERVATIONS_CSV_FILE_NAME"

# Default filename for the observations CSV uploaded to Google Drive.
DEFAULT_OBSERVATIONS_CSV_FILE_NAME = "observations.csv"

# Google Drive OAuth scope required to find, create, and replace files.
GOOGLE_DRIVE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/drive"

# Google Drive API service name.
GOOGLE_DRIVE_API_NAME = "drive"

# Google Drive API version.
GOOGLE_DRIVE_API_VERSION = "v3"

# MIME type assigned to uploaded comma-separated value files.
CSV_MIME_TYPE = "text/csv"

# Number of matching Drive files that distinguishes a duplicate-name error.
MAXIMUM_MATCHING_FILE_COUNT = 2
