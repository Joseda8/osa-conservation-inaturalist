"""Raw aggregate trend data loader.

@file trend_raw_data_loader.py
@brief Loads downloaded aggregate trend JSON files into PostgreSQL.
"""

import json
from datetime import date
from pathlib import Path
from typing import Any

from inaturalist_client.constants import DATA_DIR, RAW_DOWNLOADS_DIR_NAME, RAW_TRENDS_DIR_NAME, TREND_FILE_NAME_PREFIX
from inaturalist_client.trend_record import TrendRecord
from inaturalist_client.trend_region_config import TrendRegionConfig
from psycopg import Connection
from utils import LOGGER

from .trend_loader import TrendLoader


class TrendRawDataLoader:
    """Loads downloaded aggregate trend files into PostgreSQL.

    @param database_connection Open PostgreSQL connection.
    @param data_dir Folder containing downloaded raw data.
    @param load_date Only load trend data for this snapshot date.
    """

    def __init__(self, database_connection: Connection, data_dir: Path = DATA_DIR, load_date: str | None = None):
        """Create a raw aggregate trend data loader.

        @param database_connection Open PostgreSQL connection.
        @param data_dir Folder containing downloaded raw data.
        @param load_date Only load trend data for this snapshot date.
        """
        self._data_dir = data_dir
        self._load_date = load_date
        self._trend_loader = TrendLoader(database_connection)

    def load(self) -> int:
        """Load all available raw aggregate trend files into PostgreSQL.

        @return Number of trend records processed.
        """
        loaded_count = 0
        for trend_file_path in self._get_trend_file_paths():
            trend_records = self._read_trend_records(trend_file_path)
            LOGGER.info("Loading raw trend file into database: %s", trend_file_path)
            loaded_count += self._trend_loader.load(trend_records, str(trend_file_path))

        LOGGER.info("Loaded %s trend records from raw files", loaded_count)
        return loaded_count

    def _get_trend_file_paths(self) -> list[Path]:
        """Get raw aggregate trend files selected for loading.

        @return Sorted raw aggregate trend file paths.
        """
        trends_data_dir = self._data_dir / RAW_DOWNLOADS_DIR_NAME / RAW_TRENDS_DIR_NAME
        if self._load_date is not None:
            trend_date_dir = trends_data_dir / self._load_date
            return sorted(trend_date_dir.glob(f"{TREND_FILE_NAME_PREFIX}_{self._load_date}_*.json"))

        return sorted(trends_data_dir.glob(f"*/{TREND_FILE_NAME_PREFIX}_*.json"))

    def _read_trend_records(self, trend_file_path: Path) -> list[TrendRecord]:
        """Read and deserialize one raw aggregate trend file.

        @param trend_file_path Raw aggregate trend file path.
        @return Trend records represented by the file.
        """
        with open(trend_file_path) as input_file:
            trend_file_json = json.load(input_file)

        region_json = trend_file_json["region"]
        region_config = TrendRegionConfig(
            key=region_json["key"],
            label=region_json["label"],
            region_type=region_json["region_type"],
            request_params=region_json["request_params"],
        )
        return [
            self._deserialize_trend_record(region_config, trend_record_json)
            for trend_record_json in trend_file_json["records"]
        ]

    def _deserialize_trend_record(self, region_config: TrendRegionConfig, trend_record_json: dict[str, Any]) -> TrendRecord:
        """Build one trend record from its JSON representation.

        @param region_config Region metadata stored with the file.
        @param trend_record_json Serialized trend row.
        @return Deserialized trend record.
        """
        return TrendRecord(
            region_config=region_config,
            metric_name=trend_record_json["metric_name"],
            period_type=trend_record_json["period_type"],
            period_start=date.fromisoformat(trend_record_json["period_start"]),
            period_end=date.fromisoformat(trend_record_json["period_end"]),
            value=int(trend_record_json["value"]),
            source_endpoint=trend_record_json["source_endpoint"],
            source_params=trend_record_json["source_params"],
            dimension_type=trend_record_json["dimension_type"],
            dimension_id=trend_record_json["dimension_id"],
            dimension_label=trend_record_json["dimension_label"],
        )
