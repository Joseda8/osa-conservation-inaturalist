-- Counts OSA's requested focal bird taxa by observed date for ABS, OBS, and their deduplicated aggregate.

WITH focal_birds AS (
    SELECT *
    FROM (
        VALUES
            (14308::BIGINT, 'Chiroxiphia lanceolata'::TEXT, 'Lance-tailed Manakin'::TEXT),
            (10126::BIGINT, 'Psarocolius decumanus'::TEXT, 'Crested Oropendola'::TEXT),
            (367618::BIGINT, 'Clibanornis rubiginosus'::TEXT, 'Ruddy Foliage-gleaner'::TEXT),
            (8479::BIGINT, 'Cyanocorax affinis'::TEXT, 'Black-chested Jay'::TEXT),
            (20856::BIGINT, 'Pharomachrus mocinno'::TEXT, 'Resplendent Quetzal'::TEXT)
    ) AS focal_bird(taxon_id, scientific_name, english_name)
),
matched_project_observations AS (
    -- Include observations identified as a focal species or one of its descendant taxa.
    SELECT
        observations.project_alias,
        observations.observation_id,
        observations.observed_on,
        focal_birds.taxon_id,
        focal_birds.scientific_name,
        focal_birds.english_name
    FROM observations
    INNER JOIN taxa AS observed_taxa
        ON observed_taxa.taxon_id = observations.taxon_id
    INNER JOIN focal_birds
        ON observed_taxa.taxon_id = focal_birds.taxon_id
        OR observed_taxa.ancestor_ids @> jsonb_build_array(focal_birds.taxon_id)
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
