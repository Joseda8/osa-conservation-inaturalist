WITH referenced_taxon_ids AS (
    SELECT DISTINCT ancestor_id.value::BIGINT AS taxon_id
    FROM taxa AS source_taxa
    CROSS JOIN LATERAL jsonb_array_elements_text(
        COALESCE(source_taxa.ancestor_ids, '[]'::JSONB)
    ) AS ancestor_id(value)
)
SELECT referenced_taxon_ids.taxon_id
FROM referenced_taxon_ids
LEFT JOIN taxa AS stored_taxa
    ON stored_taxa.taxon_id = referenced_taxon_ids.taxon_id
WHERE stored_taxa.taxon_id IS NULL
ORDER BY referenced_taxon_ids.taxon_id;
