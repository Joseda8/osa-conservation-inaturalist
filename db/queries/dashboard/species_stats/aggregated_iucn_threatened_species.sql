-- Ranks research-grade species observed in ABS or OBS by their iNaturalist IUCN Red List threat level.

WITH research_grade_species_observations AS (
    -- Convert every research-grade observation to its species-level taxon.
    SELECT
        observations.project_alias,
        observations.observation_id,
        COALESCE(species_taxa.taxon_id, CASE WHEN observed_taxa.rank = 'species' THEN observed_taxa.taxon_id END) AS species_taxon_id
    FROM observations
    INNER JOIN taxa AS observed_taxa
        ON observed_taxa.taxon_id = observations.taxon_id
    LEFT JOIN LATERAL (
        SELECT lineage_taxa.taxon_id
        FROM jsonb_array_elements_text(
            COALESCE(observed_taxa.ancestor_ids, '[]'::JSONB)
        ) WITH ORDINALITY AS lineage_id(value, lineage_position)
        INNER JOIN taxa AS lineage_taxa
            ON lineage_taxa.taxon_id = lineage_id.value::BIGINT
        WHERE lineage_taxa.rank = 'species'
        ORDER BY lineage_id.lineage_position DESC
        LIMIT 1
    ) AS species_taxa ON TRUE
    WHERE observations.project_alias IN ('abs', 'obs')
        AND observations.quality_grade = 'research'
),
aggregated_species_observations AS (
    -- Count an observation shared by ABS and OBS only once.
    SELECT DISTINCT ON (observation_id)
        observation_id,
        species_taxon_id
    FROM research_grade_species_observations
    WHERE species_taxon_id IS NOT NULL
    ORDER BY
        observation_id,
        project_alias
),
iucn_threat_levels AS (
    -- iNaturalist can provide more than one IUCN Red List record for a taxon.
    -- Retain the highest threatened level supplied by that authority.
    SELECT
        taxon_id,
        MAX(iucn) AS iucn_level
    FROM taxon_conservation_statuses
    WHERE authority = 'IUCN Red List'
        AND iucn IN (30, 40, 50)
    GROUP BY taxon_id
),
threatened_species_counts AS (
    SELECT
        aggregated_species_observations.species_taxon_id,
        taxa.scientific_name,
        taxa.common_name,
        iucn_threat_levels.iucn_level,
        COUNT(*) AS observation_count
    FROM aggregated_species_observations
    INNER JOIN iucn_threat_levels
        ON iucn_threat_levels.taxon_id = aggregated_species_observations.species_taxon_id
    INNER JOIN taxa
        ON taxa.taxon_id = aggregated_species_observations.species_taxon_id
    GROUP BY
        aggregated_species_observations.species_taxon_id,
        taxa.scientific_name,
        taxa.common_name,
        iucn_threat_levels.iucn_level
)
SELECT
    'aggregated'::TEXT AS project_alias,
    ROW_NUMBER() OVER (
        ORDER BY
            iucn_level DESC,
            observation_count DESC,
            scientific_name,
            species_taxon_id
    ) AS species_rank,
    species_taxon_id,
    scientific_name,
    common_name,
    iucn_level,
    CASE iucn_level
        WHEN 50 THEN 'Critically Endangered'
        WHEN 40 THEN 'Endangered'
        WHEN 30 THEN 'Vulnerable'
    END AS iucn_category,
    observation_count
FROM threatened_species_counts
ORDER BY species_rank;
