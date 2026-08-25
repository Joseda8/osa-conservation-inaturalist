"""Project observation reconciliation.

@file project_observation_reconciler.py
@brief Deletes local observations that no longer belong to a project.
"""

from psycopg import Connection
from utils import LOGGER

from inaturalist_client.project_config import ProjectConfig

from .constants import DELETE_ORPHAN_OBSERVERS_QUERY_PATH, DELETE_ORPHAN_TAXA_QUERY_PATH, DELETE_STALE_OBSERVATION_PHOTOS_QUERY_PATH, DELETE_STALE_OBSERVATIONS_QUERY_PATH, SELECT_PROJECT_OBSERVATION_IDS_QUERY_PATH
from .query_loader import load_sql_query

class ProjectObservationReconciler:
    """Deletes local observations that no longer belong to a project.

    @param database_connection Open PostgreSQL connection.
    """

    def __init__(self, database_connection: Connection):
        """Create a project observation reconciler.

        @param database_connection Open PostgreSQL connection.
        """
        self._database_connection = database_connection

    def get_local_observation_ids(self, project_config: ProjectConfig) -> set[int]:
        """Get local observation IDs for a project.

        @param project_config Project to inspect.
        @return Local observation IDs stored in PostgreSQL.
        """
        local_observation_rows = self._database_connection.execute(load_sql_query(SELECT_PROJECT_OBSERVATION_IDS_QUERY_PATH), (project_config.alias,)).fetchall()
        LOGGER.info("Loaded %s local observation IDs for project %s from PostgreSQL", len(local_observation_rows), project_config.alias)
        return {int(local_observation_row[0]) for local_observation_row in local_observation_rows}

    def delete_stale_observations(
        self,
        project_config: ProjectConfig,
        stale_observation_ids: set[int],
    ) -> int:
        """Delete observations that no longer belong to a project.

        @param project_config Project being reconciled.
        @param stale_observation_ids Local observation IDs no longer in the project.
        @return Number of deleted observations.
        """
        LOGGER.info("Project %s has %s stale local observation IDs", project_config.alias, len(stale_observation_ids))
        if not stale_observation_ids:
            LOGGER.info("No stale observation IDs found for project %s", project_config.alias)
            LOGGER.info("Deleted 0 stale observations for project %s", project_config.alias)
            return 0

        LOGGER.info("Deleting stale observation data for project %s", project_config.alias)
        stale_observation_id_list = sorted(stale_observation_ids)
        with self._database_connection.transaction():
            deleted_observation_count = self._delete_stale_project_data(
                project_config.alias,
                stale_observation_id_list,
            )
            self._delete_orphan_observers()
            self._delete_orphan_taxa()

        LOGGER.info("Deleted %s stale observations for project %s", deleted_observation_count, project_config.alias)
        return deleted_observation_count

    def _delete_stale_project_data(
        self,
        project_alias: str,
        stale_observation_ids: list[int],
    ) -> int:
        """Delete stale observations and their project-scoped child data.

        @param project_alias Local project alias.
        @param stale_observation_ids Stale local observation IDs.
        @return Number of deleted observations.
        """
        self._delete_stale_observation_photos(project_alias, stale_observation_ids)
        deleted_observation_rows = self._database_connection.execute(load_sql_query(DELETE_STALE_OBSERVATIONS_QUERY_PATH), (project_alias, stale_observation_ids)).fetchall()
        return len(deleted_observation_rows)

    def _delete_stale_observation_photos(
        self,
        project_alias: str,
        stale_observation_ids: list[int],
    ):
        """Delete stale observation photos for a project.

        @param project_alias Local project alias.
        @param stale_observation_ids Stale local observation IDs.
        """
        self._database_connection.execute(load_sql_query(DELETE_STALE_OBSERVATION_PHOTOS_QUERY_PATH), (project_alias, stale_observation_ids))

    def _delete_orphan_observers(self):
        """Delete observers not referenced by any local observation."""
        self._database_connection.execute(load_sql_query(DELETE_ORPHAN_OBSERVERS_QUERY_PATH))

    def _delete_orphan_taxa(self):
        """Delete taxa not referenced by observations or their taxon lineages."""
        self._database_connection.execute(load_sql_query(DELETE_ORPHAN_TAXA_QUERY_PATH))
