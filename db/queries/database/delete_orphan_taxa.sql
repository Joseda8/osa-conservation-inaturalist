DELETE FROM taxa AS taxon_rows
WHERE NOT EXISTS (
    SELECT 1
    FROM observations AS observation_rows
    WHERE observation_rows.taxon_id = taxon_rows.taxon_id
)
    AND NOT EXISTS (
        SELECT 1
        FROM taxa AS observed_taxa
        WHERE observed_taxa.ancestor_ids @> jsonb_build_array(taxon_rows.taxon_id)
            AND EXISTS (
                SELECT 1
                FROM observations AS observation_rows
                WHERE observation_rows.taxon_id = observed_taxa.taxon_id
            )
    );
