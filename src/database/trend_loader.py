"""Aggregate trend loader.

@file trend_loader.py
@brief Loads iNaturalist aggregate trend rows into PostgreSQL.
"""

from inaturalist_client.trend_record import TrendRecord
from psycopg import Connection
from psycopg.types.json import Jsonb
from utils import LOGGER

from .constants import UPSERT_TREND_QUERY_PATH
from .query_loader import load_sql_query

class TrendLoader:
    """Loads aggregate iNaturalist trend rows into PostgreSQL.

    @param database_connection Open PostgreSQL connection.
    """

    def __init__(self, database_connection: Connection):
        """Create a trend loader.

        @param database_connection Open PostgreSQL connection.
        """
        self._database_connection = database_connection

    def load(self, trend_records: list[TrendRecord], loaded_from: str) -> int:
        """Load trend records into PostgreSQL.

        @param trend_records Trend records to upsert.
        @param loaded_from Source file that supplied the trend records.
        @return Number of trend records processed.
        """
        if not trend_records:
            LOGGER.info("No trend records to load")
            return 0

        with self._database_connection.transaction():
            for trend_record in trend_records:
                self._upsert_trend_record(trend_record, loaded_from)

        LOGGER.info("Loaded %s trend records into PostgreSQL", len(trend_records))
        return len(trend_records)

    def _upsert_trend_record(self, trend_record: TrendRecord, loaded_from: str):
        """Upsert one trend record.

        @param trend_record Trend record to upsert.
        @param loaded_from Source file that supplied the trend record.
        """
        region_config = trend_record.region_config
        self._database_connection.execute(
            load_sql_query(UPSERT_TREND_QUERY_PATH),
            (
                region_config.key,
                region_config.region_type,
                region_config.label,
                trend_record.metric_name,
                trend_record.period_type,
                trend_record.period_start,
                trend_record.period_end,
                trend_record.dimension_type,
                trend_record.dimension_id,
                trend_record.dimension_label,
                trend_record.value,
                trend_record.source_endpoint,
                Jsonb(trend_record.source_params),
                loaded_from,
            ),
        )
