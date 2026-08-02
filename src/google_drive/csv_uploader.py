"""Google Drive CSV uploader.

@file csv_uploader.py
@brief Uploads CSV content to a Google Drive folder.
"""

import io
import json
import os
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from .constants import CSV_MIME_TYPE, DEFAULT_GOOGLE_SERVICE_ACCOUNT_JSON_PATH, DEFAULT_OBSERVATIONS_CSV_FILE_NAME, GOOGLE_DRIVE_API_NAME, GOOGLE_DRIVE_API_VERSION, GOOGLE_DRIVE_OBSERVATIONS_CSV_FILE_NAME_ENV_VAR, GOOGLE_DRIVE_UPLOAD_FOLDER_ID_ENV_VAR, GOOGLE_DRIVE_UPLOAD_SCOPE, GOOGLE_SERVICE_ACCOUNT_JSON_ENV_VAR, GOOGLE_SERVICE_ACCOUNT_JSON_PATH_ENV_VAR, MAXIMUM_MATCHING_FILE_COUNT


class GoogleDriveCsvUploader:
    """Uploads a CSV to the configured Google Drive folder."""

    def upload_observations_csv(self, csv_content: str) -> str:
        """Create or replace the configured observations CSV file.

        @param csv_content UTF-8 CSV content to upload.
        @return Google Drive file ID.
        """
        folder_id = self._get_required_environment_variable(GOOGLE_DRIVE_UPLOAD_FOLDER_ID_ENV_VAR)
        file_name = os.environ.get(GOOGLE_DRIVE_OBSERVATIONS_CSV_FILE_NAME_ENV_VAR, DEFAULT_OBSERVATIONS_CSV_FILE_NAME)
        credentials = Credentials.from_service_account_info(
            self._get_service_account_info(),
            scopes=[GOOGLE_DRIVE_UPLOAD_SCOPE],
        )
        drive_service = build(GOOGLE_DRIVE_API_NAME, GOOGLE_DRIVE_API_VERSION, credentials=credentials)
        existing_file_id = self._find_existing_file_id(drive_service, folder_id, file_name)
        media = MediaIoBaseUpload(io.BytesIO(csv_content.encode("utf-8")), mimetype=CSV_MIME_TYPE, resumable=False)
        if existing_file_id is None:
            uploaded_file = drive_service.files().create(body={"name": file_name, "parents": [folder_id]}, media_body=media, fields="id", supportsAllDrives=True).execute()
        else:
            uploaded_file = drive_service.files().update(fileId=existing_file_id, media_body=media, fields="id", supportsAllDrives=True).execute()

        return uploaded_file["id"]

    @staticmethod
    def _get_required_environment_variable(variable_name: str) -> str:
        """Return a required environment variable value.

        @param variable_name Name of the required environment variable.
        @return Configured environment variable value.
        @raises RuntimeError If the environment variable is not set.
        """
        value = os.environ.get(variable_name)
        if not value:
            raise RuntimeError(f"Set {variable_name} in .env before uploading CSV files to Google Drive.")
        return value

    @staticmethod
    def _get_service_account_info() -> dict:
        """Load service account credentials from an environment variable or local file.

        @return Parsed Google service account credentials.
        @raises RuntimeError If no credentials source is available.
        """
        service_account_json = os.environ.get(GOOGLE_SERVICE_ACCOUNT_JSON_ENV_VAR)
        if service_account_json:
            return json.loads(service_account_json)

        credential_path = Path(os.environ.get(GOOGLE_SERVICE_ACCOUNT_JSON_PATH_ENV_VAR, DEFAULT_GOOGLE_SERVICE_ACCOUNT_JSON_PATH))
        if not credential_path.is_file():
            raise RuntimeError(f"Set {GOOGLE_SERVICE_ACCOUNT_JSON_ENV_VAR} or create the ignored credential file: {credential_path}")
        return json.loads(credential_path.read_text())

    @staticmethod
    def _find_existing_file_id(drive_service, folder_id: str, file_name: str) -> str | None:
        """Find one non-trashed file with the configured name in a Drive folder.

        @param drive_service Authenticated Google Drive client.
        @param folder_id Destination Google Drive folder ID.
        @param file_name Exact CSV filename.
        @return File ID when exactly one match exists, otherwise None.
        @raises RuntimeError If multiple matching files exist.
        """
        escaped_file_name = file_name.replace("\\", "\\\\").replace("'", "\\'")
        query = f"'{folder_id}' in parents and name = '{escaped_file_name}' and trashed = false"
        response = drive_service.files().list(q=query, fields="files(id)", pageSize=MAXIMUM_MATCHING_FILE_COUNT, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        files = response.get("files", [])
        if len(files) > 1:
            raise RuntimeError(f"Expected at most one CSV named '{file_name}' in the configured folder; found multiple.")
        if not files:
            return None

        return files[0]["id"]
