"""Aggregate trend loader.

@file trend_loader.py
@brief Loads iNaturalist aggregate trend rows into PostgreSQL.
"""

from inaturalist_client.trend_record import TrendRecord
from psycopg import Connection
from psycopg.types.json import Jsonb
from utils import LOGGER


class TrendLoader:
    """Loads aggregate iNaturalist trend rows into PostgreSQL.

    @param database_connection Open PostgreSQL connection.
    """

    def __init__(self, database_connection: Connection):
        """Create a trend loader.

        @param database_connection Open PostgreSQL connection.
        """
        self._database_connection = database_connection

    def load(self, trend_records: list[TrendRecord]) -> int:
        """Load trend records into PostgreSQL.

        @param trend_records Trend records to upsert.
        @return Number of trend records processed.
        """
        if not trend_records:
            LOGGER.info("No trend records to load")
            return 0

        with self._database_connection.transaction():
            for trend_record in trend_records:
                self._upsert_trend_record(trend_record)

        LOGGER.info("Loaded %s trend records into PostgreSQL", len(trend_records))
        return len(trend_records)

    def _upsert_trend_record(self, trend_record: TrendRecord):
        """Upsert one trend record.

        @param trend_record Trend record to upsert.
        """
        region_config = trend_record.region_config
        self._database_connection.execute(
            """
            INSERT INTO trends (
                region_key,
                region_type,
                region_label,
                metric_name,
                period_type,
                period_start,
                period_end,
                value,
                source_endpoint,
                source_params,
                raw_json,
                downloaded_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
            ON CONFLICT (region_key, metric_name, period_type, period_start)
            DO UPDATE SET
                region_type = EXCLUDED.region_type,
                region_label = EXCLUDED.region_label,
                period_end = EXCLUDED.period_end,
                value = EXCLUDED.value,
                source_endpoint = EXCLUDED.source_endpoint,
                source_params = EXCLUDED.source_params,
                raw_json = EXCLUDED.raw_json,
                downloaded_at = now()
            """,
            (
                region_config.key,
                region_config.region_type,
                region_config.label,
                trend_record.metric_name,
                trend_record.period_type,
                trend_record.period_start,
                trend_record.period_end,
                trend_record.value,
                trend_record.source_endpoint,
                Jsonb(trend_record.source_params),
                Jsonb(trend_record.raw_json),
            ),
        )
