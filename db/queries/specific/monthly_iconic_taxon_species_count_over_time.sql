-- Title: Monthly iconic taxon species count over time
-- Description: Shows how a selected iconic taxon species count changes by month and region. Configure period_start as a Metabase Field Filter mapped to trends.period_start, iconic_taxon as a Metabase Field Filter mapped to trends.dimension_label, and region_key as a Metabase Field Filter mapped to trends.region_key.

SELECT
    period_start,
    period_end,
    region_label,
    dimension_id AS taxon_id,
    dimension_label AS iconic_taxon,
    value AS species_count
FROM trends
WHERE metric_name = 'iconic_taxon_species_count'
    AND period_type = 'month'
    AND dimension_type = 'iconic_taxon'
    [[AND {{period_start}}]]
    [[AND {{iconic_taxon}}]]
    [[AND {{region_key}}]]
ORDER BY
    period_start,
    CASE region_key
        WHEN 'costa_rica' THEN 1
        WHEN 'abs' THEN 2
        WHEN 'obs' THEN 3
        ELSE 4
    END,
    iconic_taxon;
