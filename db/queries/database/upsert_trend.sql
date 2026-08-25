INSERT INTO trends (
    region_key,
    region_type,
    region_label,
    metric_name,
    period_type,
    period_start,
    period_end,
    dimension_type,
    dimension_id,
    dimension_label,
    value,
    source_endpoint,
    source_params,
    loaded_from,
    loaded_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
ON CONFLICT (
    region_key,
    metric_name,
    period_type,
    period_start,
    dimension_type,
    dimension_id
)
DO UPDATE SET
    region_type = EXCLUDED.region_type,
    region_label = EXCLUDED.region_label,
    period_end = EXCLUDED.period_end,
    dimension_label = EXCLUDED.dimension_label,
    value = EXCLUDED.value,
    source_endpoint = EXCLUDED.source_endpoint,
    source_params = EXCLUDED.source_params,
    loaded_from = EXCLUDED.loaded_from,
    loaded_at = now();
