"""iNaturalist trend record.

@file trend_record.py
@brief Defines one aggregate trend metric row.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any

from .trend_region_config import TrendRegionConfig


@dataclass(frozen=True)
class TrendRecord:
    """One aggregate iNaturalist trend metric.

    @param region_config Region represented by the trend.
    @param metric_name Metric name.
    @param period_type Time period type, such as month.
    @param period_start First date in the period.
    @param period_end Last date in the period.
    @param value Metric value.
    @param source_endpoint iNaturalist API endpoint used.
    @param source_params API parameters used.
    @param raw_json Raw source fragment for the trend row.
    @param dimension_type Optional trend dimension type.
    @param dimension_id Optional trend dimension ID.
    @param dimension_label Optional trend dimension label.
    """

    region_config: TrendRegionConfig
    metric_name: str
    period_type: str
    period_start: date
    period_end: date
    value: int
    source_endpoint: str
    source_params: dict[str, Any]
    raw_json: dict[str, Any]
    dimension_type: str = "none"
    dimension_id: str = "none"
    dimension_label: str = "none"
