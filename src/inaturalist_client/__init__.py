"""Public package interface for iNaturalist helpers.

@file __init__.py
@brief Exposes the API used by scripts and future project modules.
"""

from .client import InaturalistClient
from .constants import OSA_PROJECTS, TREND_REGIONS
from .project_config import ProjectConfig
from .project_download_summary import ProjectDownloadSummary
from .storage import JsonFileStorage
from .trend_record import TrendRecord
from .trend_region_config import TrendRegionConfig

__all__ = [
    "InaturalistClient",
    "JsonFileStorage",
    "OSA_PROJECTS",
    "ProjectConfig",
    "ProjectDownloadSummary",
    "TREND_REGIONS",
    "TrendRecord",
    "TrendRegionConfig",
]
