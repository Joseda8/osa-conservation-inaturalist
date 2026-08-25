"""Database constants.

@file constants.py
@brief Defines database defaults and paths.
"""

from pathlib import Path


# Environment variable used to override the database connection string.
DATABASE_URL_ENV_VAR = "OSA_DATABASE_URL"

# Folder containing versioned SQL migration files.
MIGRATIONS_DIR = Path("db") / "migrations"

# Folder containing production SQL queries executed by the database layer.
DATABASE_QUERIES_DIR = Path("db") / "queries" / "database"

# SQL query files used to load iNaturalist project observations.
UPSERT_PROJECT_QUERY_PATH = DATABASE_QUERIES_DIR / "upsert_project.sql"
UPSERT_OBSERVER_QUERY_PATH = DATABASE_QUERIES_DIR / "upsert_observer.sql"
UPSERT_OBSERVATION_QUERY_PATH = DATABASE_QUERIES_DIR / "upsert_observation.sql"
UPSERT_OBSERVATION_PHOTO_QUERY_PATH = DATABASE_QUERIES_DIR / "upsert_observation_photo.sql"

# SQL query files used to reconcile stored project observations.
SELECT_PROJECT_OBSERVATION_IDS_QUERY_PATH = DATABASE_QUERIES_DIR / "select_project_observation_ids.sql"
DELETE_STALE_OBSERVATIONS_QUERY_PATH = DATABASE_QUERIES_DIR / "delete_stale_observations.sql"
DELETE_STALE_OBSERVATION_PHOTOS_QUERY_PATH = DATABASE_QUERIES_DIR / "delete_stale_observation_photos.sql"
DELETE_ORPHAN_OBSERVERS_QUERY_PATH = DATABASE_QUERIES_DIR / "delete_orphan_observers.sql"
DELETE_ORPHAN_TAXA_QUERY_PATH = DATABASE_QUERIES_DIR / "delete_orphan_taxa.sql"

# SQL query file used to load aggregate iNaturalist trends.
UPSERT_TREND_QUERY_PATH = DATABASE_QUERIES_DIR / "upsert_trend.sql"

# SQL query files used to store and enrich taxonomy.
SELECT_ALL_TAXON_IDS_QUERY_PATH = DATABASE_QUERIES_DIR / "select_all_taxon_ids.sql"
SELECT_MISSING_LINEAGE_TAXON_IDS_QUERY_PATH = DATABASE_QUERIES_DIR / "select_missing_lineage_taxon_ids.sql"
UPSERT_TAXON_QUERY_PATH = DATABASE_QUERIES_DIR / "upsert_taxon.sql"

# SQL query files used to track applied database migrations.
CREATE_SCHEMA_MIGRATIONS_TABLE_QUERY_PATH = DATABASE_QUERIES_DIR / "create_schema_migrations_table.sql"
SELECT_SCHEMA_MIGRATION_VERSIONS_QUERY_PATH = DATABASE_QUERIES_DIR / "select_schema_migration_versions.sql"
INSERT_SCHEMA_MIGRATION_QUERY_PATH = DATABASE_QUERIES_DIR / "insert_schema_migration.sql"
