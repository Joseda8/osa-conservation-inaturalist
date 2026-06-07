CREATE TEMP TABLE latest_observation_keys ON COMMIT DROP AS
SELECT DISTINCT ON (project_alias, observation_id)
    project_alias,
    download_date,
    observation_id
FROM observations
ORDER BY
    project_alias,
    observation_id,
    download_date DESC,
    updated_at DESC NULLS LAST,
    loaded_at DESC;

CREATE UNIQUE INDEX idx_latest_observation_keys
    ON latest_observation_keys(project_alias, download_date, observation_id);

DELETE FROM observation_field_values AS field_values
WHERE NOT EXISTS (
    SELECT 1
    FROM latest_observation_keys AS latest
    WHERE latest.project_alias = field_values.project_alias
        AND latest.download_date = field_values.download_date
        AND latest.observation_id = field_values.observation_id
);

DELETE FROM project_observations AS project_observation_rows
WHERE NOT EXISTS (
    SELECT 1
    FROM latest_observation_keys AS latest
    WHERE latest.project_alias = project_observation_rows.project_alias
        AND latest.download_date = project_observation_rows.download_date
        AND latest.observation_id = project_observation_rows.observation_id
);

DELETE FROM observation_photos AS photos
WHERE NOT EXISTS (
    SELECT 1
    FROM latest_observation_keys AS latest
    WHERE latest.project_alias = photos.project_alias
        AND latest.download_date = photos.download_date
        AND latest.observation_id = photos.observation_id
);

DELETE FROM observations AS observation_rows
WHERE NOT EXISTS (
    SELECT 1
    FROM latest_observation_keys AS latest
    WHERE latest.project_alias = observation_rows.project_alias
        AND latest.download_date = observation_rows.download_date
        AND latest.observation_id = observation_rows.observation_id
);

ALTER TABLE observation_field_values
    DROP CONSTRAINT observation_field_values_project_alias_download_date_obser_fkey;

ALTER TABLE project_observations
    DROP CONSTRAINT project_observations_project_alias_download_date_observati_fkey;

ALTER TABLE observation_photos
    DROP CONSTRAINT observation_photos_project_alias_download_date_observation_fkey;

ALTER TABLE observations
    DROP CONSTRAINT observations_pkey;

ALTER TABLE observation_photos
    DROP CONSTRAINT observation_photos_pkey;

ALTER TABLE project_observations
    DROP CONSTRAINT project_observations_pkey;

ALTER TABLE observation_field_values
    DROP CONSTRAINT observation_field_values_pkey;

ALTER TABLE observations
    ADD CONSTRAINT observations_pkey PRIMARY KEY (project_alias, observation_id);

ALTER TABLE observation_photos
    ADD CONSTRAINT observation_photos_pkey PRIMARY KEY (project_alias, observation_id, photo_id);

ALTER TABLE observation_photos
    ADD CONSTRAINT observation_photos_project_observation_fkey
    FOREIGN KEY (project_alias, observation_id)
    REFERENCES observations(project_alias, observation_id);

ALTER TABLE project_observations
    ADD CONSTRAINT project_observations_pkey PRIMARY KEY (project_alias, project_observation_id);

ALTER TABLE project_observations
    ADD CONSTRAINT project_observations_project_observation_fkey
    FOREIGN KEY (project_alias, observation_id)
    REFERENCES observations(project_alias, observation_id);

ALTER TABLE observation_field_values
    ADD CONSTRAINT observation_field_values_pkey PRIMARY KEY (project_alias, observation_id, ofv_index);

ALTER TABLE observation_field_values
    ADD CONSTRAINT observation_field_values_project_observation_fkey
    FOREIGN KEY (project_alias, observation_id)
    REFERENCES observations(project_alias, observation_id);
