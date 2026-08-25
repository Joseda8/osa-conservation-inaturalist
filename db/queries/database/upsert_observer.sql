INSERT INTO observers (
    observer_id,
    login,
    name,
    observations_count,
    species_count,
    loaded_from,
    loaded_at
)
VALUES (%s, %s, %s, %s, %s, %s, now())
ON CONFLICT (observer_id) DO UPDATE SET
    login = EXCLUDED.login,
    name = EXCLUDED.name,
    observations_count = EXCLUDED.observations_count,
    species_count = EXCLUDED.species_count,
    loaded_from = EXCLUDED.loaded_from,
    loaded_at = now();
