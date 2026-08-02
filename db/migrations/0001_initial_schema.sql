-- OSA Conservation iNaturalist database migration 0001: baseline schema.
-- Apply this script once to an empty PostgreSQL database.

CREATE TABLE projects (
    alias TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL
);

CREATE TABLE taxa (
    taxon_id BIGINT PRIMARY KEY,
    scientific_name TEXT,
    common_name TEXT,
    rank TEXT,
    rank_level NUMERIC,
    parent_id BIGINT,
    ancestor_ids JSONB,
    iconic_taxon_id BIGINT,
    iconic_taxon_name TEXT,
    is_active BOOLEAN,
    native BOOLEAN,
    introduced BOOLEAN,
    endemic BOOLEAN,
    threatened BOOLEAN,
    extinct BOOLEAN,
    loaded_from TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE observers (
    observer_id BIGINT PRIMARY KEY,
    login TEXT,
    name TEXT,
    observations_count INTEGER,
    species_count INTEGER,
    loaded_from TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE observations (
    project_alias TEXT NOT NULL REFERENCES projects(alias),
    download_date DATE NOT NULL,
    observation_id BIGINT NOT NULL,
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
    taxon_id BIGINT REFERENCES taxa(taxon_id),
    observer_id BIGINT REFERENCES observers(observer_id),
    loaded_from TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (project_alias, observation_id)
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
    loaded_from TEXT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (project_alias, observation_id, photo_id),
    FOREIGN KEY (project_alias, observation_id)
        REFERENCES observations(project_alias, observation_id)
);

CREATE TABLE trends (
    region_key TEXT NOT NULL,
    region_type TEXT NOT NULL,
    region_label TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    period_type TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    dimension_type TEXT NOT NULL DEFAULT 'none',
    dimension_id TEXT NOT NULL DEFAULT 'none',
    dimension_label TEXT NOT NULL DEFAULT 'none',
    value NUMERIC NOT NULL,
    source_endpoint TEXT NOT NULL,
    source_params JSONB NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (
        region_key,
        metric_name,
        period_type,
        period_start,
        dimension_type,
        dimension_id
    )
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

CREATE INDEX idx_trends_metric_period
    ON trends(metric_name, period_type, period_start, period_end);

CREATE INDEX idx_trends_region_period
    ON trends(region_key, period_type, period_start, period_end);

CREATE INDEX idx_trends_dimension
    ON trends(dimension_type, dimension_id);
