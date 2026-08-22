"""GitHub Pages refresh pipeline step.

@file refresh_github_pages_step.py
@brief Writes the observations CSV source for the GitHub Pages refresh workflow.
"""

from google_drive import GoogleDriveCsvReader
from pipeline.constants import ABS_VS_OBS_REPORTS, GITHUB_PAGES_DATA_DIRECTORY
from pipeline.pipeline_context import PipelineContext
from utils import LOGGER


class RefreshGitHubPagesStep:
    """Refreshes GitHub Pages source data from the observations CSV."""

    name = "refresh-github-pages"

    def run(self, pipeline_context: PipelineContext):
        """Read dashboard CSV reports and save them for the React build.

        @param pipeline_context Shared pipeline state.
        """
        GITHUB_PAGES_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        google_drive_reader = GoogleDriveCsvReader()
        for file_name, _ in ABS_VS_OBS_REPORTS:
            output_path = GITHUB_PAGES_DATA_DIRECTORY / file_name
            output_path.write_text(google_drive_reader.read_csv(file_name), encoding="utf-8")
            LOGGER.info("Saved Google Drive report for GitHub Pages: %s", output_path)
