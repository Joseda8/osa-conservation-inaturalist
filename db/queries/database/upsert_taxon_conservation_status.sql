INSERT INTO taxon_conservation_statuses (
    conservation_status_id,
    taxon_id,
    place_id,
    source_id,
    user_id,
    authority,
    status,
    status_name,
    geoprivacy,
    iucn,
    loaded_from,
    loaded_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
ON CONFLICT (conservation_status_id) DO UPDATE SET
    taxon_id = EXCLUDED.taxon_id,
    place_id = EXCLUDED.place_id,
    source_id = EXCLUDED.source_id,
    user_id = EXCLUDED.user_id,
    authority = EXCLUDED.authority,
    status = EXCLUDED.status,
    status_name = EXCLUDED.status_name,
    geoprivacy = EXCLUDED.geoprivacy,
    iucn = EXCLUDED.iucn,
    loaded_from = EXCLUDED.loaded_from,
    loaded_at = now();
