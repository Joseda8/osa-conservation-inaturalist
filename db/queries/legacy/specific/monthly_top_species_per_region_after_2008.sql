-- Title: Monthly top species per region after 2008
-- Description: Shows the top species by observation count for each month and region after 2008. Change top_n to adjust the number of rows per region and month.

WITH query_parameters AS (
    SELECT 5 AS top_n
),
ranked_species AS (
    SELECT
        region_key,
        region_label,
        period_start,
        period_end,
        dimension_id AS taxon_id,
        dimension_label AS species,
        value AS observation_count,
        ROW_NUMBER() OVER (
            PARTITION BY region_key, period_start
            ORDER BY value DESC, dimension_label
        ) AS taxon_rank
    FROM trends
    WHERE metric_name = 'species_observation_count'
        AND period_type = 'month'
        AND dimension_type = 'species_taxon'
        AND period_start >= DATE '2009-01-01'
)
SELECT
    period_start,
    period_end,
    taxon_rank,
    region_label,
    species,
    observation_count
FROM ranked_species
WHERE taxon_rank <= (SELECT top_n FROM query_parameters)
ORDER BY
    period_start,
    taxon_rank,
    CASE region_key
        WHEN 'costa_rica' THEN 1
        WHEN 'abs' THEN 2
        WHEN 'obs' THEN 3
        ELSE 4
    END,
    species;
