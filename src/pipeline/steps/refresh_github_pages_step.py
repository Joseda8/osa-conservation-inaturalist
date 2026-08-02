"""GitHub Pages refresh pipeline step.

@file refresh_github_pages_step.py
@brief Writes the observations CSV source for the GitHub Pages refresh workflow.
"""

from google_drive import GoogleDriveCsvReader
from pipeline.constants import GITHUB_PAGES_OBSERVATIONS_CSV_PATH
from pipeline.pipeline_context import PipelineContext
from utils import LOGGER


class RefreshGitHubPagesStep:
    """Refreshes GitHub Pages source data from the observations CSV."""

    name = "refresh-github-pages"

    def run(self, pipeline_context: PipelineContext):
        """Read the observations CSV and save it for the React build.

        @param pipeline_context Shared pipeline state.
        """
        csv_content = GoogleDriveCsvReader().read_observations_csv()
        GITHUB_PAGES_OBSERVATIONS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        GITHUB_PAGES_OBSERVATIONS_CSV_PATH.write_text(csv_content, encoding="utf-8")
        LOGGER.info("Saved Google Drive CSV for GitHub Pages: %s", GITHUB_PAGES_OBSERVATIONS_CSV_PATH)
