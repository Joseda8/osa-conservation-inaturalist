"""Pipeline context.

@file pipeline_context.py
@brief Defines shared state passed between pipeline steps.
"""

from dataclasses import dataclass, field
from datetime import date, datetime

from inaturalist_client import InaturalistClient
from inaturalist_client.project_config import ProjectConfig
from inaturalist_client.project_download_summary import ProjectDownloadSummary


@dataclass
class PipelineContext:
    """Shared state passed between pipeline steps.

    @param project_configs Projects processed by the pipeline.
    @param per_page Requested observation batch size.
    @param request_cooldown_seconds Seconds to wait after successful requests.
    @param failure_cooldown_seconds Seconds to wait after failed requests.
    @param download_mode Raw data download mode.
    @param updated_since Only download observations updated since this time.
    @param load_date Only load raw data for this snapshot date.
    @param trend_mode Trend download mode.
    @param trend_period_start First date of the monthly trend period range to download.
    @param trend_period_end Last date of the monthly trend period range to download.
    @param inaturalist_client Client used to download iNaturalist data.
    @param download_summaries Download summaries created by the download step.
    """

    project_configs: tuple[ProjectConfig, ...]
    per_page: int
    request_cooldown_seconds: float
    failure_cooldown_seconds: float
    download_mode: str
    updated_since: datetime | str | None = None
    load_date: str | None = None
    trend_mode: str = "since"
    trend_period_start: date | None = None
    trend_period_end: date | None = None
    inaturalist_client: InaturalistClient | None = None
    download_summaries: list[ProjectDownloadSummary] = field(default_factory=list)

    def get_inaturalist_client(self) -> InaturalistClient:
        """Get the iNaturalist client, creating it only when needed.

        @return iNaturalist client.
        """
        if self.inaturalist_client is None:
            self.inaturalist_client = InaturalistClient()

        return self.inaturalist_client
