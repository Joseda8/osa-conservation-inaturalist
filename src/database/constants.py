"""Database constants.

@file constants.py
@brief Defines database defaults and paths.
"""

from pathlib import Path


# Default PostgreSQL connection string for the local Docker Compose database.
DEFAULT_DATABASE_URL = "postgresql://osa:osa@localhost:5432/osa_inaturalist"

# Environment variable used to override the database connection string.
DATABASE_URL_ENV_VAR = "OSA_DATABASE_URL"

# Folder containing versioned SQL migration files.
MIGRATIONS_DIR = Path("db") / "migrations"
