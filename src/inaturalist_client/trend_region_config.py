"""iNaturalist trend region configuration.

@file trend_region_config.py
@brief Defines source regions used for aggregate trend downloads.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TrendRegionConfig:
    """Configuration for an aggregate iNaturalist trend region.

    @param key Short local key used in trend tables.
    @param label Human-readable region label.
    @param region_type Region source type, such as project or place.
    @param request_params iNaturalist API filters for this region.
    """

    key: str
    label: str
    region_type: str
    request_params: dict[str, Any]
