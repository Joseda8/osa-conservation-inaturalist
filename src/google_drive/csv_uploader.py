"""Google Drive CSV uploader.

@file csv_uploader.py
@brief Uploads CSV content to a Google Drive folder.
"""

import io
import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from .constants import CSV_MIME_TYPE, GOOGLE_DRIVE_API_NAME, GOOGLE_DRIVE_API_VERSION, GOOGLE_DRIVE_FOLDER_MIME_TYPE, GOOGLE_DRIVE_UPLOAD_FOLDER_ID_ENV_VAR, MAXIMUM_MATCHING_FILE_COUNT
from .oauth_credentials import GoogleDriveOAuthCredentials


class GoogleDriveCsvUploader:
    """Uploads a CSV to the configured Google Drive folder."""

    def upload_csv(self, file_name: str, csv_content: str, dated_folder_name: str) -> str:
        """Create or replace a CSV file in one dated Google Drive folder.

        @param csv_content UTF-8 CSV content to upload.
        @param file_name Destination CSV filename.
        @param dated_folder_name Destination subfolder name formatted as YYYYMMDD.
        @return Google Drive file ID.
        """
        processed_data_folder_id = self._get_required_environment_variable(GOOGLE_DRIVE_UPLOAD_FOLDER_ID_ENV_VAR)
        credentials = GoogleDriveOAuthCredentials().get()
        drive_service = build(GOOGLE_DRIVE_API_NAME, GOOGLE_DRIVE_API_VERSION, credentials=credentials)
        dated_folder_id = self._get_or_create_dated_folder_id(drive_service, processed_data_folder_id, dated_folder_name)
        existing_file_id = self._find_existing_file_id(drive_service, dated_folder_id, file_name)
        media = MediaIoBaseUpload(io.BytesIO(csv_content.encode("utf-8")), mimetype=CSV_MIME_TYPE, resumable=False)
        if existing_file_id is None:
            uploaded_file = drive_service.files().create(body={"name": file_name, "parents": [dated_folder_id]}, media_body=media, fields="id", supportsAllDrives=True).execute()
        else:
            uploaded_file = drive_service.files().update(fileId=existing_file_id, media_body=media, fields="id", supportsAllDrives=True).execute()

        return uploaded_file["id"]

    def _get_or_create_dated_folder_id(self, drive_service, processed_data_folder_id: str, dated_folder_name: str) -> str:
        """Find or create the one Drive folder for a report generation date.

        @param drive_service Authenticated Google Drive client.
        @param processed_data_folder_id Configured root processed-data folder ID.
        @param dated_folder_name Destination subfolder name formatted as YYYYMMDD.
        @return Google Drive ID of the dated subfolder.
        """
        dated_folder_id = self._find_dated_folder_id(drive_service, processed_data_folder_id, dated_folder_name)
        if dated_folder_id:
            return dated_folder_id
        created_folder = drive_service.files().create(body={"name": dated_folder_name, "mimeType": GOOGLE_DRIVE_FOLDER_MIME_TYPE, "parents": [processed_data_folder_id]}, fields="id", supportsAllDrives=True).execute()
        return created_folder["id"]

    @staticmethod
    def _find_dated_folder_id(drive_service, processed_data_folder_id: str, dated_folder_name: str) -> str | None:
        """Find one non-trashed dated subfolder of processed-data.

        @param drive_service Authenticated Google Drive client.
        @param processed_data_folder_id Configured root processed-data folder ID.
        @param dated_folder_name Subfolder name formatted as YYYYMMDD.
        @return Google Drive folder ID when it exists, otherwise None.
        @raises RuntimeError If the date identifies multiple folders.
        """
        escaped_folder_name = dated_folder_name.replace("\\", "\\\\").replace("'", "\\'")
        query = f"'{processed_data_folder_id}' in parents and name = '{escaped_folder_name}' and mimeType = '{GOOGLE_DRIVE_FOLDER_MIME_TYPE}' and trashed = false"
        response = drive_service.files().list(q=query, fields="files(id)", pageSize=MAXIMUM_MATCHING_FILE_COUNT, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        folders = response.get("files", [])
        if len(folders) > 1:
            raise RuntimeError(f"Expected at most one dated folder named '{dated_folder_name}' in the configured processed-data folder; found multiple.")
        return folders[0]["id"] if folders else None

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
