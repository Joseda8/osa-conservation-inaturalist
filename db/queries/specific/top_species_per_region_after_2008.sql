-- Title: Top species per region after 2008
-- Description: Shows the top species by summed monthly observation count for each region after 2008. Change top_n to adjust the number of rows per region.

WITH query_parameters AS (
    SELECT 5 AS top_n
),
species_counts AS (
    SELECT
        region_key,
        region_label,
        dimension_id AS taxon_id,
        dimension_label AS species,
        SUM(value) AS observation_count
    FROM trends
    WHERE metric_name = 'species_observation_count'
        AND period_type = 'month'
        AND dimension_type = 'species_taxon'
        AND period_start >= DATE '2009-01-01'
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
        species,
        observation_count,
        ROW_NUMBER() OVER (
            PARTITION BY region_key
            ORDER BY observation_count DESC, species
        ) AS taxon_rank
    FROM species_counts
)
SELECT
    taxon_rank,
    region_label,
    species,
    observation_count
FROM ranked_species
WHERE taxon_rank <= (SELECT top_n FROM query_parameters)
ORDER BY
    taxon_rank,
    CASE region_key
        WHEN 'costa_rica' THEN 1
        WHEN 'abs' THEN 2
        WHEN 'obs' THEN 3
        ELSE 4
    END,
    species;
