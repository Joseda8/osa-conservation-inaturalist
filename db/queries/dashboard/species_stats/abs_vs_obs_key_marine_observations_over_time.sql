-- Counts OSA's requested focal marine taxa by observed date for ABS, OBS, and their deduplicated aggregate.

WITH focal_marine_taxa AS (
    SELECT *
    FROM (
        VALUES
            (41566::BIGINT, 'Megaptera novaeangliae'::TEXT, 'Humpback Whale'::TEXT),
            (39672::BIGINT, 'Eretmochelys imbricata'::TEXT, 'Hawksbill Sea Turtle'::TEXT),
            (41482::BIGINT, 'Tursiops truncatus'::TEXT, 'Common Bottlenose Dolphin'::TEXT),
            (776566::BIGINT, 'Hydrophis platurus xanthos'::TEXT, 'Yellow Sea Snake'::TEXT),
            (516508::BIGINT, 'Scarinae'::TEXT, 'Parrotfishes'::TEXT)
    ) AS focal_taxon(taxon_id, scientific_name, english_name)
),
matched_project_observations AS (
    -- Include observations identified as a focal taxon or one of its descendant taxa.
    SELECT
        observations.project_alias,
        observations.observation_id,
        observations.observed_on,
        focal_marine_taxa.taxon_id,
        focal_marine_taxa.scientific_name,
        focal_marine_taxa.english_name
    FROM observations
    INNER JOIN taxa AS observed_taxa
        ON observed_taxa.taxon_id = observations.taxon_id
    INNER JOIN focal_marine_taxa
        ON observed_taxa.taxon_id = focal_marine_taxa.taxon_id
        OR observed_taxa.ancestor_ids @> jsonb_build_array(focal_marine_taxa.taxon_id)
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
