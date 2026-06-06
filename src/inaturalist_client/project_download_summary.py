"""Project download summary.

@file project_download_summary.py
@brief Defines the result returned by project downloads.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectDownloadSummary:
    """Summary of a project observation download.

    @param project_alias Short local project alias.
    @param download_date Date string used for the data version.
    @param page_count Number of downloaded API pages.
    @param total_results Total observations reported by iNaturalist.
    @param saved_file_paths JSON files written during the download.
    """

    project_alias: str
    download_date: str
    page_count: int
    total_results: int
    saved_file_paths: list[Path]
