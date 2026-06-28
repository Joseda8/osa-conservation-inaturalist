-- Title: Top 25 most observed insect orders by project
-- Description: Shows the top 25 insect observation ranks by taxonomic order for ABS and OBS. Coarser identifications remain grouped under their current taxon.

WITH classified_observations AS (
    SELECT
        observations.project_alias,
        COALESCE(order_taxa.taxon_id, observed_taxa.taxon_id) AS taxon_id,
        COALESCE(order_taxa.scientific_name, observed_taxa.scientific_name) AS scientific_name,
        COALESCE(order_taxa.common_name, observed_taxa.common_name) AS common_name,
        COALESCE(order_taxa.rank, observed_taxa.rank) AS grouping_rank
    FROM observations
    INNER JOIN taxa AS observed_taxa
        ON observed_taxa.taxon_id = observations.taxon_id
    LEFT JOIN LATERAL (
        SELECT lineage_taxa.*
        FROM jsonb_array_elements_text(
            COALESCE(observed_taxa.ancestor_ids, '[]'::JSONB)
        ) WITH ORDINALITY AS lineage_id(value, lineage_position)
        INNER JOIN taxa AS lineage_taxa
            ON lineage_taxa.taxon_id = lineage_id.value::BIGINT
        WHERE lineage_taxa.rank = 'order'
        ORDER BY lineage_id.lineage_position DESC
        LIMIT 1
    ) AS order_taxa ON TRUE
    WHERE observed_taxa.iconic_taxon_name = 'Insecta'
),
taxon_counts AS (
    SELECT
        project_alias,
        taxon_id,
        scientific_name,
        common_name,
        grouping_rank,
        COUNT(*) AS observation_count
    FROM classified_observations
    GROUP BY
        project_alias,
        taxon_id,
        scientific_name,
        common_name,
        grouping_rank
),
ranked_taxa AS (
    SELECT
        DENSE_RANK() OVER (
            PARTITION BY project_alias
            ORDER BY observation_count DESC
        ) AS project_rank,
        project_alias,
        taxon_id,
        scientific_name,
        common_name,
        grouping_rank,
        observation_count
    FROM taxon_counts
)
SELECT
    project_rank,
    project_alias,
    taxon_id,
    scientific_name,
    common_name,
    grouping_rank,
    observation_count
FROM ranked_taxa
WHERE project_rank <= 25
ORDER BY
    project_alias,
    project_rank,
    scientific_name;
