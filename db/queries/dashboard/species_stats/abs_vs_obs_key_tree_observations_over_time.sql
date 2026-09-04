-- Counts OSA's requested focal tree taxa by observed date for ABS, OBS, and their deduplicated aggregate.

WITH focal_trees AS (
    SELECT *
    FROM (
        VALUES
            (190315::BIGINT, 'Caryocar costaricense'::TEXT, 'Costa Rican Garlic Tree'::TEXT),
            (189310::BIGINT, 'Anthodiscus chocoensis'::TEXT, 'Chocó Anthodiscus'::TEXT),
            (185878::BIGINT, 'Minquartia guianensis'::TEXT, 'Black Manwood'::TEXT),
            (910767::BIGINT, 'Peltogyne purpurea'::TEXT, 'Purpleheart'::TEXT),
            (440806::BIGINT, 'Mora oleifera'::TEXT, 'Mora Tree'::TEXT)
    ) AS focal_taxon(taxon_id, scientific_name, english_name)
),
matched_project_observations AS (
    -- Include observations identified as a focal species or one of its descendant taxa.
    SELECT
        observations.project_alias,
        observations.observation_id,
        observations.observed_on,
        focal_trees.taxon_id,
        focal_trees.scientific_name,
        focal_trees.english_name
    FROM observations
    INNER JOIN taxa AS observed_taxa
        ON observed_taxa.taxon_id = observations.taxon_id
    INNER JOIN focal_trees
        ON observed_taxa.taxon_id = focal_trees.taxon_id
        OR observed_taxa.ancestor_ids @> jsonb_build_array(focal_trees.taxon_id)
    WHERE observations.project_alias IN ('abs', 'obs')
        AND observations.observed_on IS NOT NULL
),
project_counts AS (
    SELECT
        project_alias,
        observed_on AS observed_date,
        taxon_id,
        scientific_name,
        english_name,
        COUNT(*) AS observation_count
    FROM matched_project_observations
    GROUP BY
        project_alias,
        observed_on,
        taxon_id,
        scientific_name,
        english_name
),
aggregated_counts AS (
    -- The same iNaturalist observation can belong to both projects; count it once here.
    SELECT
        'aggregated'::TEXT AS project_alias,
        observed_on AS observed_date,
        taxon_id,
        scientific_name,
        english_name,
        COUNT(DISTINCT observation_id) AS observation_count
    FROM matched_project_observations
    GROUP BY
        observed_on,
        taxon_id,
        scientific_name,
        english_name
)
SELECT
    project_alias,
    observed_date,
    taxon_id,
    scientific_name,
    english_name,
    observation_count
FROM project_counts
UNION ALL
SELECT
    project_alias,
    observed_date,
    taxon_id,
    scientific_name,
    english_name,
    observation_count
FROM aggregated_counts
ORDER BY
    observed_date,
    taxon_id,
    project_alias;
