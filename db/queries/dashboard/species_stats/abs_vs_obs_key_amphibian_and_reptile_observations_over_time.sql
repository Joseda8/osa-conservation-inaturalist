-- Counts OSA's requested focal amphibian and reptile taxa by observed date for ABS, OBS, and their deduplicated aggregate.

WITH focal_amphibians_and_reptiles AS (
    SELECT *
    FROM (
        VALUES
            (23702::BIGINT, 'Agalychnis callidryas'::TEXT, 'Red-eyed Tree Frog'::TEXT),
            (21121::BIGINT, 'Dendrobates auratus'::TEXT, 'Green-and-black Poison Dart Frog'::TEXT),
            (21214::BIGINT, 'Phyllobates vittatus'::TEXT, 'Golfo Dulce Poison Dart Frog'::TEXT),
            (30844::BIGINT, 'Bothriechis schlegelii'::TEXT, 'Highland Eyelash-Pitviper'::TEXT),
            (31049::BIGINT, 'Lachesis melanocephala'::TEXT, 'Black-headed Bushmaster'::TEXT)
    ) AS focal_taxon(taxon_id, scientific_name, english_name)
),
matched_project_observations AS (
    -- Include observations identified as a focal species or one of its descendant taxa.
    SELECT
        observations.project_alias,
        observations.observation_id,
        observations.observed_on,
        focal_amphibians_and_reptiles.taxon_id,
        focal_amphibians_and_reptiles.scientific_name,
        focal_amphibians_and_reptiles.english_name
    FROM observations
    INNER JOIN taxa AS observed_taxa
        ON observed_taxa.taxon_id = observations.taxon_id
    INNER JOIN focal_amphibians_and_reptiles
        ON observed_taxa.taxon_id = focal_amphibians_and_reptiles.taxon_id
        OR observed_taxa.ancestor_ids @> jsonb_build_array(focal_amphibians_and_reptiles.taxon_id)
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
