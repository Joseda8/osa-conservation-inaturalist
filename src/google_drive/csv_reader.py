"""Google Drive CSV reader.

@file csv_reader.py
@brief Reads observations CSV content from a Google Drive folder.
"""

import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from .constants import GOOGLE_DRIVE_API_NAME, GOOGLE_DRIVE_API_VERSION, GOOGLE_DRIVE_UPLOAD_FOLDER_ID_ENV_VAR, MAXIMUM_MATCHING_FILE_COUNT
from .oauth_credentials import GoogleDriveOAuthCredentials


class GoogleDriveCsvReader:
    """Reads a CSV from the configured Google Drive folder."""

    def read_csv(self, file_name: str) -> str:
        """Read a CSV file from the configured Google Drive folder.

        @param file_name Exact CSV filename.
        @return UTF-8 CSV content.
        """
        folder_id = self._get_required_environment_variable(GOOGLE_DRIVE_UPLOAD_FOLDER_ID_ENV_VAR)
        credentials = GoogleDriveOAuthCredentials().get()
        drive_service = build(GOOGLE_DRIVE_API_NAME, GOOGLE_DRIVE_API_VERSION, credentials=credentials)
        file_id = self._find_file_id(drive_service, folder_id, file_name)
        request = drive_service.files().get_media(fileId=file_id, supportsAllDrives=True)
        download_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(download_buffer, request)
        is_complete = False
        while not is_complete:
            _, is_complete = downloader.next_chunk()

        return download_buffer.getvalue().decode("utf-8-sig")

    @staticmethod
    def _get_required_environment_variable(variable_name: str) -> str:
        """Return a required environment variable value.

        @param variable_name Name of the required environment variable.
        @return Configured environment variable value.
        @raises RuntimeError If the environment variable is not set.
        """
        value = os.environ.get(variable_name)
        if not value:
            raise RuntimeError(f"Set {variable_name} before reading CSV files from Google Drive.")
        return value

    @staticmethod
    def _find_file_id(drive_service, folder_id: str, file_name: str) -> str:
        """Find exactly one non-trashed CSV file in a Drive folder.

        @param drive_service Authenticated Google Drive client.
        @param folder_id Destination Google Drive folder ID.
        @param file_name Exact CSV filename.
        @return CSV file ID.
        @raises RuntimeError If the filename does not identify exactly one file.
        """
        escaped_file_name = file_name.replace("\\", "\\\\").replace("'", "\\'")
        query = f"'{folder_id}' in parents and name = '{escaped_file_name}' and trashed = false"
        response = drive_service.files().list(q=query, fields="files(id)", pageSize=MAXIMUM_MATCHING_FILE_COUNT, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()
        files = response.get("files", [])
        if len(files) != 1:
            raise RuntimeError(f"Expected exactly one CSV named '{file_name}' in the configured folder; found {len(files)}.")
        return files[0]["id"]
