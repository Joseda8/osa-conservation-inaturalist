"""Database migration pipeline step.

@file migrate_database_step.py
@brief Applies pending PostgreSQL migrations.
"""

from database import MigrationRunner, open_database_connection
from pipeline.pipeline_context import PipelineContext


class MigrateDatabaseStep:
    """Pipeline step that applies pending database migrations."""

    name = "migrate-db"

    def run(self, pipeline_context: PipelineContext):
        """Apply pending database migrations.

        @param pipeline_context Shared pipeline state.
        """
        with open_database_connection() as database_connection:
            MigrationRunner(database_connection).run()
