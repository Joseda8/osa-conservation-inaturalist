-- Title: Monthly observation trends by region
-- Description: Shows observed-date monthly iNaturalist observation counts for configured trend regions. Configure period_start as a Metabase Field Filter mapped to trends.period_start.

SELECT
    region_key,
    region_label,
    period_start,
    period_end,
    value AS observations
FROM trends
WHERE metric_name = 'observation_count'
    AND period_type = 'month'
    [[AND {{period_start}}]]
ORDER BY
    period_start,
    region_key;
