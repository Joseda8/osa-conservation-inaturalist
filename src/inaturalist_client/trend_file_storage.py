"""Aggregate trend file storage.

@file trend_file_storage.py
@brief Stores downloaded aggregate trend records as reloadable JSON files.
"""

from datetime import date
from pathlib import Path

from .constants import DATA_DIR, RAW_DOWNLOADS_DIR_NAME, RAW_TRENDS_DIR_NAME, TREND_FILE_NAME_PREFIX
from .storage import JsonFileStorage
from .trend_record import TrendRecord


class TrendFileStorage(JsonFileStorage):
    """Stores aggregate trend records in the raw data tree.

    @param storage_dir Directory containing downloaded data.
    """

    def __init__(self, storage_dir: Path = DATA_DIR):
        """Create trend file storage.

        @param storage_dir Directory containing downloaded data.
        """
        super().__init__(storage_dir)

    def save(self, trend_records: list[TrendRecord], download_date: date | None = None) -> Path:
        """Save one region and metric's trend records as a raw data file.

        @param trend_records Records for exactly one region and metric.
        @param download_date Date used to version the downloaded file.
        @return Path to the saved JSON file.
        """
        if not trend_records:
            raise ValueError("Cannot save a trend file without records")

        first_trend_record = trend_records[0]
        self._validate_records(trend_records, first_trend_record)
        date_version = (download_date or date.today()).strftime("%Y%m%d")
        file_path = self._get_file_path(first_trend_record, date_version)
        return self._save_json(file_path, self._serialize_records(trend_records))

    def _validate_records(self, trend_records: list[TrendRecord], first_trend_record: TrendRecord):
        """Ensure a file contains one consistent region and metric.

        @param trend_records Records selected for storage.
        @param first_trend_record Record defining the expected region and metric.
        """
        for trend_record in trend_records:
            if trend_record.region_config != first_trend_record.region_config or trend_record.metric_name != first_trend_record.metric_name:
                raise ValueError("A trend file must contain one region and metric")

    def _get_file_path(self, trend_record: TrendRecord, date_version: str) -> Path:
        """Build the raw trend file path relative to the data directory.

        @param trend_record Record identifying the region and metric.
        @param date_version Download date formatted as YYYYMMDD.
        @return Relative raw trend file path.
        """
        file_name = f"{TREND_FILE_NAME_PREFIX}_{date_version}_{trend_record.region_config.key}_{trend_record.metric_name}.json"
        return Path(RAW_DOWNLOADS_DIR_NAME) / RAW_TRENDS_DIR_NAME / date_version / file_name

    def _serialize_records(self, trend_records: list[TrendRecord]) -> dict:
        """Convert trend records to the reloadable JSON file format.

        @param trend_records Records to serialize.
        @return JSON-serializable raw trend file content.
        """
        region_config = trend_records[0].region_config
        return {
            "region": {
                "key": region_config.key,
                "label": region_config.label,
                "region_type": region_config.region_type,
                "request_params": region_config.request_params,
            },
            "records": [
                {
                    "metric_name": trend_record.metric_name,
                    "period_type": trend_record.period_type,
                    "period_start": trend_record.period_start.isoformat(),
                    "period_end": trend_record.period_end.isoformat(),
                    "value": trend_record.value,
                    "source_endpoint": trend_record.source_endpoint,
                    "source_params": trend_record.source_params,
                    "dimension_type": trend_record.dimension_type,
                    "dimension_id": trend_record.dimension_id,
                    "dimension_label": trend_record.dimension_label,
                }
                for trend_record in trend_records
            ],
        }
