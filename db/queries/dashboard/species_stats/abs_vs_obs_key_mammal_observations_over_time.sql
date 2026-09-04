-- Counts OSA's requested focal mammal taxa by observed date for ABS, OBS, and their deduplicated aggregate.

WITH focal_mammals AS (
    SELECT *
    FROM (
        VALUES
            (42007::BIGINT, 'Puma concolor'::TEXT, 'Puma'::TEXT, 'Puma'::TEXT),
            (43411::BIGINT, 'Ateles geoffroyi'::TEXT, 'Central American Spider Monkey'::TEXT, 'Mono colorado'::TEXT),
            (43355::BIGINT, 'Tapirus bairdii'::TEXT, 'Baird''s Tapir'::TEXT, 'Danta'::TEXT),
            (41970::BIGINT, 'Panthera onca'::TEXT, 'Jaguar'::TEXT, 'Jaguar'::TEXT),
            (42115::BIGINT, 'Tayassu pecari'::TEXT, 'White-lipped Peccary'::TEXT, 'Chancho de monte'::TEXT)
    ) AS focal_mammal(taxon_id, scientific_name, english_name, spanish_name)
),
matched_project_observations AS (
    -- Include observations identified as a focal species or one of its descendant taxa.
    SELECT
        observations.project_alias,
        observations.observation_id,
        observations.observed_on,
        focal_mammals.taxon_id,
        focal_mammals.scientific_name,
        focal_mammals.english_name,
        focal_mammals.spanish_name
    FROM observations
    INNER JOIN taxa AS observed_taxa
        ON observed_taxa.taxon_id = observations.taxon_id
    INNER JOIN focal_mammals
        ON observed_taxa.taxon_id = focal_mammals.taxon_id
        OR observed_taxa.ancestor_ids @> jsonb_build_array(focal_mammals.taxon_id)
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
        spanish_name,
        COUNT(*) AS observation_count
    FROM matched_project_observations
    GROUP BY
        project_alias,
        observed_on,
        taxon_id,
        scientific_name,
        english_name,
        spanish_name
),
aggregated_counts AS (
    -- The same iNaturalist observation can belong to both projects; count it once here.
    SELECT
        'aggregated'::TEXT AS project_alias,
        observed_on AS observed_date,
        taxon_id,
        scientific_name,
        english_name,
        spanish_name,
        COUNT(DISTINCT observation_id) AS observation_count
    FROM matched_project_observations
    GROUP BY
        observed_on,
        taxon_id,
        scientific_name,
        english_name,
        spanish_name
)
SELECT
    project_alias,
    observed_date,
    taxon_id,
    scientific_name,
    english_name,
    spanish_name,
    observation_count
FROM project_counts
UNION ALL
SELECT
    project_alias,
    observed_date,
    taxon_id,
    scientific_name,
    english_name,
    spanish_name,
    observation_count
FROM aggregated_counts
ORDER BY
    observed_date,
    taxon_id,
    project_alias;
