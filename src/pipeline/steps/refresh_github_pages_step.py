"""GitHub Pages refresh pipeline step.

@file refresh_github_pages_step.py
@brief Reads the observations CSV source for the GitHub Pages refresh workflow.
"""

from google_drive import GoogleDriveCsvReader
from pipeline.pipeline_context import PipelineContext


class RefreshGitHubPagesStep:
    """Refreshes GitHub Pages source data from the observations CSV."""

    name = "refresh-github-pages"

    def run(self, pipeline_context: PipelineContext):
        """Read and print the complete observations CSV source.

        @param pipeline_context Shared pipeline state.
        """
        csv_content = GoogleDriveCsvReader().read_observations_csv()
        print(csv_content, end="" if csv_content.endswith("\n") else "\n")
