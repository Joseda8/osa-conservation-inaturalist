-- Lists the five most-observed species in ABS, OBS, and Costa Rica separately.
-- All counts come directly from iNaturalist monthly species-count trends.

WITH region_species_counts AS (
    SELECT
        trends.region_key,
        trends.region_label,
        trends.dimension_id::BIGINT AS species_taxon_id,
        COALESCE(taxa.scientific_name, trends.dimension_label) AS scientific_name,
        COALESCE(taxa.common_name, trends.dimension_label) AS common_name,
        SUM(trends.value)::BIGINT AS observation_count
    FROM trends
    LEFT JOIN taxa
        ON taxa.taxon_id::TEXT = trends.dimension_id
    WHERE trends.region_key IN ('abs', 'obs', 'costa_rica')
        AND trends.metric_name = 'species_observation_count'
        AND trends.period_type = 'month'
        AND trends.dimension_type = 'species_taxon'
    GROUP BY
        trends.region_key,
        trends.region_label,
        trends.dimension_id,
        trends.dimension_label,
        taxa.scientific_name,
        taxa.common_name
),
ranked_species_counts AS (
    SELECT
        region_key,
        region_label,
        species_taxon_id,
        scientific_name,
        common_name,
        observation_count,
        ROW_NUMBER() OVER (
            PARTITION BY region_key
            ORDER BY
                observation_count DESC,
                scientific_name,
                species_taxon_id
        ) AS species_rank
    FROM region_species_counts
)
SELECT
    region_key,
    region_label,
    species_rank,
    species_taxon_id,
    scientific_name,
    common_name,
    observation_count
FROM ranked_species_counts
WHERE species_rank <= 5
ORDER BY
    CASE region_key
        WHEN 'abs' THEN 1
        WHEN 'obs' THEN 2
        WHEN 'costa_rica' THEN 3
    END,
    species_rank;
