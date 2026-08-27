"""Database analysis and Google Drive upload pipeline step.

@file analyze_and_upload_to_drive_step.py
@brief Exports database analysis results to CSV and uploads the file to Google Drive.
"""

import csv
import io
from datetime import date
from pathlib import Path

from database import load_sql_query, open_database_connection
from google_drive import GoogleDriveCsvUploader
from pipeline.constants import ABS_VS_OBS_REPORTS, PROCESSED_DATA_DATE_FORMAT, PROCESSED_DATA_DIRECTORY
from pipeline.pipeline_context import PipelineContext
from utils import LOGGER


class AnalyzeAndUploadToDriveStep:
    """Pipeline step that exports database analysis results locally and to Google Drive."""

    name = "analyze-and-upload-to-drive"

    def run(self, pipeline_context: PipelineContext):
        """Run the current analysis, write CSV reports locally, and upload them to Google Drive.

        @param pipeline_context Shared pipeline state.
        """
        output_directory = PROCESSED_DATA_DIRECTORY / date.today().strftime(PROCESSED_DATA_DATE_FORMAT)
        output_directory.mkdir(parents=True, exist_ok=True)
        report_paths = self._write_reports(output_directory)
        self._upload_reports(report_paths, output_directory)

    @staticmethod
    def _upload_reports(report_paths: list[Path], output_directory: Path):
        """Upload locally generated reports when Google Drive credentials are available.

        @param report_paths Locally generated CSV report paths.
        @param output_directory Directory containing the generated reports.
        """
        google_drive_uploader = GoogleDriveCsvUploader()
        try:
            for report_path in report_paths:
                file_id = google_drive_uploader.upload_csv(report_path.name, report_path.read_text(encoding="utf-8"), output_directory.name)
                LOGGER.info("Uploaded Google Drive report %s with file ID: %s", report_path.name, file_id)
        except RuntimeError as error:
            LOGGER.warning("Skipped Google Drive upload: %s Local reports are available in: %s", error, output_directory)

    def _write_reports(self, output_directory: Path) -> list[Path]:
        """Write all database analysis CSV reports to one dated local folder.

        @param output_directory Directory for the current date's report files.
        @return Paths of the written CSV report files.
        """
        report_paths = []
        for file_name, query_path in ABS_VS_OBS_REPORTS:
            report_path = output_directory / file_name
            report_path.write_text(self._get_csv(query_path), encoding="utf-8")
            report_paths.append(report_path)
            LOGGER.info("Generated local report: %s", report_path)
        return report_paths

    @staticmethod
    def _get_csv(query_path: Path) -> str:
        """Export one SQL query result as UTF-8 CSV content.

        @return CSV content with a header row.
        """
        with open_database_connection() as database_connection:
            with database_connection.cursor() as database_cursor:
                database_cursor.execute(load_sql_query(query_path))
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerow([column.name for column in database_cursor.description])
                csv_writer.writerows(database_cursor)
                return csv_buffer.getvalue()
