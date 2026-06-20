"""Aggregate trends download pipeline step.

@file download_trends_step.py
@brief Downloads iNaturalist aggregate trend metrics into PostgreSQL.
"""

from database import TrendLoader, open_database_connection
from inaturalist_client.constants import TREND_REGIONS
from inaturalist_client.trend_record import TrendRecord
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
                observation_trend_records = inaturalist_client.get_monthly_observation_trends(
                    trend_region_config,
                    period_start=pipeline_context.trend_period_start,
                    period_end=pipeline_context.trend_period_end,
                    failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
                )
                trend_loader.load(observation_trend_records)

                for observation_trend_record in self._get_non_empty_months(
                    observation_trend_records
                ):
                    species_trend_records = inaturalist_client.get_monthly_species_count_trends(
                        trend_region_config,
                        period_start=observation_trend_record.period_start,
                        period_end=observation_trend_record.period_end,
                        failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
                    )
                    iconic_taxa_trend_records = (
                        inaturalist_client.get_monthly_iconic_taxa_count_trends(
                            trend_region_config,
                            period_start=observation_trend_record.period_start,
                            period_end=observation_trend_record.period_end,
                            failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
                        )
                    )
                    trend_loader.load(species_trend_records + iconic_taxa_trend_records)

    def _get_non_empty_months(
        self,
        observation_trend_records: list[TrendRecord],
    ) -> list[TrendRecord]:
        """Get observation trend rows for months with at least one observation.

        @param observation_trend_records Observation trend records.
        @return Trend records for non-empty months.
        """
        return [
            trend_record
            for trend_record in observation_trend_records
            if trend_record.value > 0
        ]
