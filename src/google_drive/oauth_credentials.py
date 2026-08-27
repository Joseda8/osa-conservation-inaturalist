"""OAuth credentials for Google Drive operations.

@file oauth_credentials.py
@brief Loads OAuth credentials for local and GitHub Actions Drive access.
"""

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .constants import DEFAULT_GOOGLE_DRIVE_OAUTH_CLIENT_JSON_PATH, DEFAULT_GOOGLE_DRIVE_OAUTH_TOKEN_PATH, GOOGLE_DRIVE_OAUTH_CLIENT_JSON_PATH_ENV_VAR, GOOGLE_DRIVE_OAUTH_TOKEN_JSON_ENV_VAR, GOOGLE_DRIVE_OAUTH_TOKEN_PATH_ENV_VAR, GOOGLE_DRIVE_SCOPE, GOOGLE_DRIVE_OAUTH_LOCAL_SERVER_PORT, PRIVATE_CREDENTIAL_FILE_MODE


class GoogleDriveOAuthCredentials:
    """Loads OAuth credentials for the Google user selected during authorization."""

    def get(self) -> Credentials:
        """Return valid existing credentials without opening a browser.

        @return Valid OAuth credentials.
        @raises RuntimeError If Google authorization has not been completed.
        """
        credentials = self._get_valid_credentials()
        if credentials:
            return credentials
        if os.environ.get(GOOGLE_DRIVE_OAUTH_TOKEN_JSON_ENV_VAR):
            raise RuntimeError(f"The OAuth token in {GOOGLE_DRIVE_OAUTH_TOKEN_JSON_ENV_VAR} is invalid or expired. Authorize again locally and update the GitHub Actions secret.")
        raise RuntimeError("Google authorization is required. Run --pipeline auth-with-google before accessing Google Drive.")

    def authorize(self) -> Credentials:
        """Return valid credentials or open the local Google authorization flow.

        @return Valid OAuth credentials.
        @raises RuntimeError If an invalid GitHub Actions token is present.
        """
        credentials = self._get_valid_credentials()
        if credentials:
            return credentials
        if os.environ.get(GOOGLE_DRIVE_OAUTH_TOKEN_JSON_ENV_VAR):
            raise RuntimeError(f"The OAuth token in {GOOGLE_DRIVE_OAUTH_TOKEN_JSON_ENV_VAR} is invalid or expired. Authorize again locally and update the GitHub Actions secret.")
        return self._authorize_locally()

    @classmethod
    def _get_valid_credentials(cls) -> Credentials | None:
        """Load and refresh stored OAuth credentials when possible.

        @return Valid stored credentials, if available.
        """
        credentials = cls._load_credentials()
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        return credentials if credentials and credentials.valid else None

    @staticmethod
    def _load_credentials() -> Credentials | None:
        """Load OAuth credentials from an environment variable or local token file.

        @return Stored OAuth credentials, if available.
        """
        token_json = os.environ.get(GOOGLE_DRIVE_OAUTH_TOKEN_JSON_ENV_VAR)
        if token_json:
            return Credentials.from_authorized_user_info(json.loads(token_json), [GOOGLE_DRIVE_SCOPE])
        token_path = Path(os.environ.get(GOOGLE_DRIVE_OAUTH_TOKEN_PATH_ENV_VAR, DEFAULT_GOOGLE_DRIVE_OAUTH_TOKEN_PATH))
        return Credentials.from_authorized_user_file(token_path, [GOOGLE_DRIVE_SCOPE]) if token_path.is_file() else None

    @staticmethod
    def _authorize_locally() -> Credentials:
        """Open a browser to authorize the Google user and save their refresh token.

        @return Newly authorized OAuth credentials.
        @raises RuntimeError If the local OAuth client JSON is unavailable.
        """
        client_json_path = Path(os.environ.get(GOOGLE_DRIVE_OAUTH_CLIENT_JSON_PATH_ENV_VAR, DEFAULT_GOOGLE_DRIVE_OAUTH_CLIENT_JSON_PATH))
        if not client_json_path.is_file():
            raise RuntimeError(f"Create the ignored OAuth client credential file: {client_json_path}")
        credentials = InstalledAppFlow.from_client_secrets_file(client_json_path, [GOOGLE_DRIVE_SCOPE]).run_local_server(port=GOOGLE_DRIVE_OAUTH_LOCAL_SERVER_PORT)
        token_path = Path(os.environ.get(GOOGLE_DRIVE_OAUTH_TOKEN_PATH_ENV_VAR, DEFAULT_GOOGLE_DRIVE_OAUTH_TOKEN_PATH))
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(credentials.to_json())
        token_path.chmod(PRIVATE_CREDENTIAL_FILE_MODE)
        return credentials
