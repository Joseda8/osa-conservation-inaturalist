UPDATE taxa
SET conservation_statuses_loaded_at = now()
WHERE taxon_id = %s;
