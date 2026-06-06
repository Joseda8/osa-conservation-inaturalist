"""iNaturalist project configuration.

@file project_config.py
@brief Defines source project configuration.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectConfig:
    """Configuration for a source iNaturalist project.

    @param alias Short local name used in data folders and file names.
    @param slug iNaturalist project slug used for API queries.
    """

    alias: str
    slug: str
