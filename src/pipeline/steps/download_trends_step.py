"""Aggregate trends download pipeline step.

@file download_trends_step.py
@brief Downloads iNaturalist aggregate trend metrics into PostgreSQL.
"""

from database import TrendLoader, open_database_connection
from inaturalist_client.constants import TREND_REGIONS
from pipeline.pipeline_context import PipelineContext


class DownloadTrendsStep:
    """Pipeline step that downloads aggregate iNaturalist trends."""

    name = "download-trends"

    def run(self, pipeline_context: PipelineContext):
        """Download configured aggregate trends and load them into PostgreSQL.

        @param pipeline_context Shared pipeline state.
        """
        if pipeline_context.trend_mode == "since" and (
            pipeline_context.trend_period_start is None
            or pipeline_context.trend_period_end is None
        ):
            raise ValueError("since trend mode requires --trend-year and --trend-month")

        inaturalist_client = pipeline_context.get_inaturalist_client()
        with open_database_connection() as database_connection:
            trend_loader = TrendLoader(database_connection)
            for trend_region_config in TREND_REGIONS:
                trend_records = inaturalist_client.get_monthly_observation_trends(
                    trend_region_config,
                    period_start=pipeline_context.trend_period_start,
                    period_end=pipeline_context.trend_period_end,
                    failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
                )
                trend_loader.load(trend_records)
