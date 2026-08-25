"""Database migration runner.

@file migration_runner.py
@brief Applies versioned SQL migrations to PostgreSQL.
"""

from pathlib import Path

from psycopg import Connection
from utils import LOGGER

from .constants import CREATE_SCHEMA_MIGRATIONS_TABLE_QUERY_PATH, INSERT_SCHEMA_MIGRATION_QUERY_PATH, MIGRATIONS_DIR, SELECT_SCHEMA_MIGRATION_VERSIONS_QUERY_PATH
from .query_loader import load_sql_query


class MigrationRunner:
    """Applies pending SQL migrations.

    @param database_connection Open PostgreSQL connection.
    @param migrations_dir Directory containing migration SQL files.
    """

    def __init__(self, database_connection: Connection, migrations_dir: Path = MIGRATIONS_DIR):
        """Create a migration runner.

        @param database_connection Open PostgreSQL connection.
        @param migrations_dir Directory containing migration SQL files.
        """
        self._database_connection = database_connection
        self._migrations_dir = migrations_dir

    def run(self) -> int:
        """Apply pending migrations in filename order.

        @return Number of migrations applied.
        """
        self._ensure_schema_migrations_table()
        applied_versions = self._get_applied_versions()
        applied_count = 0

        for migration_path in self._get_migration_paths():
            migration_version = self._get_migration_version(migration_path)
            if migration_version in applied_versions:
                LOGGER.info("Skipping already applied migration: %s", migration_path.name)
                continue

            LOGGER.info("Applying database migration: %s", migration_path.name)
            self._apply_migration(migration_path, migration_version)
            applied_count += 1

        LOGGER.info("Applied %s database migrations", applied_count)
        return applied_count

    def _ensure_schema_migrations_table(self):
        """Create the migration tracking table when needed."""
        self._database_connection.execute(load_sql_query(CREATE_SCHEMA_MIGRATIONS_TABLE_QUERY_PATH))
        self._database_connection.commit()

    def _get_applied_versions(self) -> set[str]:
        """Get migration versions already applied to the database.

        @return Applied migration versions.
        """
        migration_rows = self._database_connection.execute(load_sql_query(SELECT_SCHEMA_MIGRATION_VERSIONS_QUERY_PATH))
        applied_versions = {migration_row[0] for migration_row in migration_rows}
        self._database_connection.commit()
        return applied_versions

    def _get_migration_paths(self) -> list[Path]:
        """Get migration SQL files in apply order.

        @return Ordered migration file paths.
        """
        return sorted(self._migrations_dir.glob("*.sql"))

    def _get_migration_version(self, migration_path: Path) -> str:
        """Get a migration version from its file name.

        @param migration_path Migration file path.
        @return Migration version.
        """
        return migration_path.name.split("_", 1)[0]

    def _apply_migration(self, migration_path: Path, migration_version: str):
        """Apply a single migration in a transaction.

        @param migration_path Migration file path.
        @param migration_version Migration version.
        """
        migration_sql = load_sql_query(migration_path)
        with self._database_connection.transaction():
            self._database_connection.execute(migration_sql)
            self._database_connection.execute(load_sql_query(INSERT_SCHEMA_MIGRATION_QUERY_PATH), (migration_version, migration_path.name))
