"""Pipeline context.

@file pipeline_context.py
@brief Defines shared state passed between pipeline steps.
"""

from dataclasses import dataclass, field

from inaturalist_client import InaturalistClient
from inaturalist_client.project_config import ProjectConfig
from inaturalist_client.project_download_summary import ProjectDownloadSummary


@dataclass
class PipelineContext:
    """Shared state passed between pipeline steps.

    @param project_configs Projects processed by the pipeline.
    @param inaturalist_client Client used to download iNaturalist data.
    @param per_page Requested observation batch size.
    @param request_cooldown_seconds Seconds to wait after successful requests.
    @param failure_cooldown_seconds Seconds to wait after failed requests.
    @param minimum_per_page Smallest batch size allowed after failures.
    @param download_summaries Download summaries created by the download step.
    """

    project_configs: tuple[ProjectConfig, ...]
    inaturalist_client: InaturalistClient
    per_page: int
    request_cooldown_seconds: float
    failure_cooldown_seconds: float
    minimum_per_page: int
    download_summaries: list[ProjectDownloadSummary] = field(default_factory=list)
