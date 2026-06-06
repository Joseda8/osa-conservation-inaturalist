CREATE TABLE projects (
    alias TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL
);

CREATE TABLE raw_observation_pages (
    project_alias TEXT NOT NULL REFERENCES projects(alias),
    download_date DATE NOT NULL,
    page_number INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    api_total_results INTEGER,
    api_page INTEGER,
    api_per_page INTEGER,
    result_count INTEGER NOT NULL,
    first_observation_id BIGINT,
    last_observation_id BIGINT,
    raw_json JSONB NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (project_alias, download_date, page_number)
);

CREATE TABLE taxa (
    taxon_id BIGINT PRIMARY KEY,
    scientific_name TEXT,
    common_name TEXT,
    rank TEXT,
    rank_level NUMERIC,
    parent_id BIGINT,
    ancestor_ids JSONB,
    ancestry TEXT,
    iconic_taxon_id BIGINT,
    iconic_taxon_name TEXT,
    is_active BOOLEAN,
    native BOOLEAN,
    introduced BOOLEAN,
    endemic BOOLEAN,
    threatened BOOLEAN,
    extinct BOOLEAN,
    raw_json JSONB NOT NULL
);

CREATE TABLE observers (
    observer_id BIGINT PRIMARY KEY,
    login TEXT,
    name TEXT,
    observations_count INTEGER,
    species_count INTEGER,
    raw_json JSONB NOT NULL
);

CREATE TABLE observations (
    project_alias TEXT NOT NULL REFERENCES projects(alias),
    download_date DATE NOT NULL,
    observation_id BIGINT NOT NULL,
    uuid UUID,
    uri TEXT,
    quality_grade TEXT,
    species_guess TEXT,
    observed_on DATE,
    observed_year INTEGER,
    observed_month INTEGER,
    observed_day INTEGER,
    created_at TIMESTAMPTZ,
    created_year INTEGER,
    created_month INTEGER,
    created_day INTEGER,
    updated_at TIMESTAMPTZ,
    time_zone_offset TEXT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    location TEXT,
    place_guess TEXT,
    positional_accuracy INTEGER,
    public_positional_accuracy INTEGER,
    geoprivacy TEXT,
    taxon_geoprivacy TEXT,
    obscured BOOLEAN,
    mappable BOOLEAN,
    captive BOOLEAN,
    project_ids JSONB,
    project_ids_with_curator_id JSONB,
    project_ids_without_curator_id JSONB,
    identifications_count INTEGER,
    num_identification_agreements INTEGER,
    num_identification_disagreements INTEGER,
    comments_count INTEGER,
    faves_count INTEGER,
    taxon_id BIGINT REFERENCES taxa(taxon_id),
    observer_id BIGINT REFERENCES observers(observer_id),
    raw_json JSONB NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (project_alias, download_date, observation_id)
);

CREATE TABLE observation_photos (
    project_alias TEXT NOT NULL,
    download_date DATE NOT NULL,
    observation_id BIGINT NOT NULL,
    photo_id BIGINT NOT NULL,
    url TEXT,
    license_code TEXT,
    attribution TEXT,
    hidden BOOLEAN,
    width INTEGER,
    height INTEGER,
    raw_json JSONB NOT NULL,
    PRIMARY KEY (project_alias, download_date, observation_id, photo_id),
    FOREIGN KEY (project_alias, download_date, observation_id)
        REFERENCES observations(project_alias, download_date, observation_id)
);

CREATE TABLE project_observations (
    project_alias TEXT NOT NULL,
    download_date DATE NOT NULL,
    project_observation_id BIGINT NOT NULL,
    observation_id BIGINT NOT NULL,
    uuid UUID,
    inat_project_id BIGINT,
    preferences_json JSONB,
    raw_json JSONB NOT NULL,
    PRIMARY KEY (project_alias, download_date, project_observation_id),
    FOREIGN KEY (project_alias, download_date, observation_id)
        REFERENCES observations(project_alias, download_date, observation_id)
);

CREATE TABLE observation_field_values (
    project_alias TEXT NOT NULL,
    download_date DATE NOT NULL,
    observation_id BIGINT NOT NULL,
    ofv_index INTEGER NOT NULL,
    field_id BIGINT,
    field_name TEXT,
    value TEXT,
    raw_json JSONB NOT NULL,
    PRIMARY KEY (project_alias, download_date, observation_id, ofv_index),
    FOREIGN KEY (project_alias, download_date, observation_id)
        REFERENCES observations(project_alias, download_date, observation_id)
);

CREATE INDEX idx_observations_project_date
    ON observations(project_alias, download_date);

CREATE INDEX idx_observations_observed_on
    ON observations(observed_on);

CREATE INDEX idx_observations_quality_grade
    ON observations(quality_grade);

CREATE INDEX idx_observations_taxon_id
    ON observations(taxon_id);

CREATE INDEX idx_observations_observer_id
    ON observations(observer_id);

CREATE INDEX idx_observations_latitude_longitude
    ON observations(latitude, longitude);

CREATE INDEX idx_taxa_iconic_taxon_name
    ON taxa(iconic_taxon_name);

CREATE INDEX idx_observation_field_values_field_name
    ON observation_field_values(field_name);
