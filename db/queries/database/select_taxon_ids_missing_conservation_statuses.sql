SELECT taxon_id
FROM taxa
WHERE conservation_statuses_loaded_at IS NULL
ORDER BY taxon_id;
