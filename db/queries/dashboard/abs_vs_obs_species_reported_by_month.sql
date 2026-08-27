-- Counts distinct species reported in each month for each OSA project and both combined.

WITH project_species_trends AS (
    SELECT
        region_key AS project_alias,
        period_start,
        period_end,
        dimension_id
    FROM trends
    WHERE region_key IN ('abs', 'obs')
        AND metric_name = 'species_observation_count'
        AND period_type = 'month'
        AND dimension_type = 'species_taxon'
),
project_species_counts AS (
    SELECT
        project_alias,
        period_start,
        period_end,
        COUNT(DISTINCT dimension_id) AS species_count
    FROM project_species_trends
    GROUP BY
        project_alias,
        period_start,
        period_end
),
aggregated_species_counts AS (
    SELECT
        'aggregated'::TEXT AS project_alias,
        period_start,
        period_end,
        COUNT(DISTINCT dimension_id) AS species_count
    FROM project_species_trends
    GROUP BY
        period_start,
        period_end
)
SELECT
    project_alias,
    period_start,
    period_end,
    species_count
FROM project_species_counts
UNION ALL
SELECT
    project_alias,
    period_start,
    period_end,
    species_count
FROM aggregated_species_counts
ORDER BY
    period_start,
    project_alias;
