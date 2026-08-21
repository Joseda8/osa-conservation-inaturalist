"""Google Drive integration constants.

@file constants.py
@brief Defines Google Drive upload configuration values.
"""

from pathlib import Path


# Required environment variable containing the destination Google Drive folder ID.
GOOGLE_DRIVE_UPLOAD_FOLDER_ID_ENV_VAR = "GOOGLE_DRIVE_UPLOAD_FOLDER_ID"

# Optional environment variable overriding the local OAuth client JSON path.
GOOGLE_DRIVE_OAUTH_CLIENT_JSON_PATH_ENV_VAR = "GOOGLE_DRIVE_OAUTH_CLIENT_JSON_PATH"

# Default ignored local path containing the OAuth desktop client JSON.
DEFAULT_GOOGLE_DRIVE_OAUTH_CLIENT_JSON_PATH = Path(".secrets") / "google-oauth-client.json"

# Environment variable containing the OAuth refresh token JSON for GitHub Actions.
GOOGLE_DRIVE_OAUTH_TOKEN_JSON_ENV_VAR = "GOOGLE_DRIVE_OAUTH_TOKEN_JSON"

# Optional environment variable overriding the local OAuth refresh token path.
GOOGLE_DRIVE_OAUTH_TOKEN_PATH_ENV_VAR = "GOOGLE_DRIVE_OAUTH_TOKEN_PATH"

# Default ignored local path containing the OAuth refresh token JSON.
DEFAULT_GOOGLE_DRIVE_OAUTH_TOKEN_PATH = Path(".secrets") / "google-oauth-token.json"

# Local TCP port value that asks the OAuth library to select an available port.
GOOGLE_DRIVE_OAUTH_LOCAL_SERVER_PORT = 0

# File permissions that restrict locally saved OAuth credentials to their owner.
PRIVATE_CREDENTIAL_FILE_MODE = 0o600

# Optional environment variable overriding the uploaded observations CSV filename.
GOOGLE_DRIVE_OBSERVATIONS_CSV_FILE_NAME_ENV_VAR = "GOOGLE_DRIVE_OBSERVATIONS_CSV_FILE_NAME"

# Default filename for the observations CSV uploaded to Google Drive.
DEFAULT_OBSERVATIONS_CSV_FILE_NAME = "observations.csv"

# Google Drive OAuth scope required to read, create, and replace generated files.
GOOGLE_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"

# Google Drive API service name.
GOOGLE_DRIVE_API_NAME = "drive"

# Google Drive API version.
GOOGLE_DRIVE_API_VERSION = "v3"

# MIME type assigned to uploaded comma-separated value files.
CSV_MIME_TYPE = "text/csv"

# Number of matching Drive files that distinguishes a duplicate-name error.
MAXIMUM_MATCHING_FILE_COUNT = 2
