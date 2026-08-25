INSERT INTO observation_photos (
    project_alias,
    download_date,
    observation_id,
    photo_id,
    url,
    license_code,
    attribution,
    hidden,
    width,
    height,
    loaded_from,
    loaded_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
ON CONFLICT (project_alias, observation_id, photo_id) DO UPDATE SET
    download_date = EXCLUDED.download_date,
    url = EXCLUDED.url,
    license_code = EXCLUDED.license_code,
    attribution = EXCLUDED.attribution,
    hidden = EXCLUDED.hidden,
    width = EXCLUDED.width,
    height = EXCLUDED.height,
    loaded_from = EXCLUDED.loaded_from,
    loaded_at = now();
