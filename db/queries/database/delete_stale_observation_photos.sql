DELETE FROM observation_photos AS photos
WHERE photos.project_alias = %s
    AND photos.observation_id = ANY(%s);
