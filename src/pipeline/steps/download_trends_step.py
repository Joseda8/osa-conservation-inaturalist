"""Aggregate trends download pipeline step.

@file download_trends_step.py
@brief Downloads iNaturalist aggregate trend metrics into raw JSON files.
"""

from datetime import date

from inaturalist_client import TrendFileStorage
from inaturalist_client.constants import TREND_REGIONS
from inaturalist_client.trend_record import TrendRecord
from pipeline.pipeline_context import PipelineContext


class DownloadTrendsStep:
    """Pipeline step that downloads aggregate iNaturalist trends to files."""

    name = "download-trends"

    def run(self, pipeline_context: PipelineContext):
        """Download configured aggregate trends and store them as raw JSON.

        @param pipeline_context Shared pipeline state.
        """
        if pipeline_context.trend_mode == "since" and (
            pipeline_context.trend_period_start is None
            or pipeline_context.trend_period_end is None
        ):
            raise ValueError("since trend mode requires --trend-year and --trend-month")

        inaturalist_client = pipeline_context.get_inaturalist_client()
        trend_file_storage = TrendFileStorage()
        download_date = date.today()
        for trend_region_config in TREND_REGIONS:
            # Observation counts establish which months contain activity in this region.
            observation_trend_records = inaturalist_client.get_monthly_observation_trends(
                trend_region_config,
                period_start=pipeline_context.trend_period_start,
                period_end=pipeline_context.trend_period_end,
                failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
            )
            if observation_trend_records:
                trend_file_storage.save(observation_trend_records, download_date)

            species_trend_records: list[TrendRecord] = []
            iconic_taxa_trend_records: list[TrendRecord] = []
            # The species and iconic-taxa endpoints are queried only for active months.
            # Empty months cannot add useful counts and would make unnecessary API requests.
            for observation_trend_record in self._get_non_empty_months(
                observation_trend_records
            ):
                species_trend_records.extend(
                    inaturalist_client.get_monthly_species_count_trends(
                        trend_region_config,
                        period_start=observation_trend_record.period_start,
                        period_end=observation_trend_record.period_end,
                        failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
                    )
                )
                iconic_taxa_trend_records.extend(
                    inaturalist_client.get_monthly_iconic_taxa_count_trends(
                        trend_region_config,
                        period_start=observation_trend_record.period_start,
                        period_end=observation_trend_record.period_end,
                        failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
                    )
                )

            if species_trend_records:
                trend_file_storage.save(species_trend_records, download_date)
            if iconic_taxa_trend_records:
                trend_file_storage.save(iconic_taxa_trend_records, download_date)

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
