-- Title: Top species counts by region
-- Description: Shows the top species by summed monthly observation count for a selected observed-date timespan. Configure period_start as a Metabase Field Filter mapped to trends.period_start, region_key as a Metabase Field Filter mapped to trends.region_key, and top_n as an optional Number variable.

WITH species_counts AS (
    SELECT
        region_key,
        region_label,
        dimension_id AS taxon_id,
        dimension_label AS taxon_name,
        SUM(value) AS observations
    FROM trends
    WHERE metric_name = 'species_observation_count'
        AND period_type = 'month'
        AND dimension_type = 'species_taxon'
        [[AND {{period_start}}]]
        [[AND {{region_key}}]]
    GROUP BY
        region_key,
        region_label,
        dimension_id,
        dimension_label
),
ranked_species AS (
    SELECT
        region_key,
        region_label,
        taxon_id,
        taxon_name,
        observations,
        ROW_NUMBER() OVER (
            PARTITION BY region_key
            ORDER BY observations DESC, taxon_name
        ) AS taxon_rank
    FROM species_counts
)
SELECT
    region_key,
    region_label,
    taxon_id,
    taxon_name,
    observations
FROM ranked_species
WHERE taxon_rank <= [[{{top_n}} --]] 5
ORDER BY
    taxon_rank,
    region_key;
