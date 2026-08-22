"""Database analysis and Google Drive upload pipeline step.

@file analyze_and_upload_to_drive_step.py
@brief Exports database analysis results to CSV and uploads the file to Google Drive.
"""

import csv
import io
from pathlib import Path

from database import open_database_connection
from google_drive import GoogleDriveCsvUploader
from pipeline.constants import ABS_VS_OBS_REPORTS
from pipeline.pipeline_context import PipelineContext
from utils import LOGGER


class AnalyzeAndUploadToDriveStep:
    """Pipeline step that exports database analysis results to Google Drive."""

    name = "analyze-and-upload-to-drive"

    def run(self, pipeline_context: PipelineContext):
        """Run the current analysis, export it to CSV, and upload it to Google Drive.

        @param pipeline_context Shared pipeline state.
        """
        google_drive_uploader = GoogleDriveCsvUploader()
        for file_name, query_path in ABS_VS_OBS_REPORTS:
            file_id = google_drive_uploader.upload_csv(file_name, self._get_csv(query_path))
            LOGGER.info("Uploaded Google Drive report %s with file ID: %s", file_name, file_id)

    @staticmethod
    def _get_csv(query_path: Path) -> str:
        """Export one SQL query result as UTF-8 CSV content.

        @return CSV content with a header row.
        """
        with open_database_connection() as database_connection:
            with database_connection.cursor() as database_cursor:
                database_cursor.execute(query_path.read_text())
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerow([column.name for column in database_cursor.description])
                csv_writer.writerows(database_cursor)
                return csv_buffer.getvalue()
