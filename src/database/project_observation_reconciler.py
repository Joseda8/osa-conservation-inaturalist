"""Project observation reconciliation.

@file project_observation_reconciler.py
@brief Deletes local observations that no longer belong to a project.
"""

from psycopg import Connection
from utils import LOGGER

from inaturalist_client.project_config import ProjectConfig


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
        local_observation_rows = self._database_connection.execute(
            """
            SELECT observation_id
            FROM observations
            WHERE project_alias = %s
            """,
            (project_config.alias,),
        ).fetchall()
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
        self._delete_stale_observation_field_values(project_alias, stale_observation_ids)
        self._delete_stale_project_observations(project_alias, stale_observation_ids)
        self._delete_stale_observation_photos(project_alias, stale_observation_ids)
        deleted_observation_rows = self._database_connection.execute(
            """
            DELETE FROM observations AS observation_rows
            WHERE observation_rows.project_alias = %s
                AND observation_rows.observation_id = ANY(%s)
            RETURNING observation_rows.observation_id
            """,
            (project_alias, stale_observation_ids),
        ).fetchall()
        return len(deleted_observation_rows)

    def _delete_stale_observation_field_values(
        self,
        project_alias: str,
        stale_observation_ids: list[int],
    ):
        """Delete stale observation field values for a project.

        @param project_alias Local project alias.
        @param stale_observation_ids Stale local observation IDs.
        """
        self._database_connection.execute(
            """
            DELETE FROM observation_field_values AS field_values
            WHERE field_values.project_alias = %s
                AND field_values.observation_id = ANY(%s)
            """,
            (project_alias, stale_observation_ids),
        )

    def _delete_stale_project_observations(
        self,
        project_alias: str,
        stale_observation_ids: list[int],
    ):
        """Delete stale project observation relations for a project.

        @param project_alias Local project alias.
        @param stale_observation_ids Stale local observation IDs.
        """
        self._database_connection.execute(
            """
            DELETE FROM project_observations AS project_observation_rows
            WHERE project_observation_rows.project_alias = %s
                AND project_observation_rows.observation_id = ANY(%s)
            """,
            (project_alias, stale_observation_ids),
        )

    def _delete_stale_observation_photos(
        self,
        project_alias: str,
        stale_observation_ids: list[int],
    ):
        """Delete stale observation photos for a project.

        @param project_alias Local project alias.
        @param stale_observation_ids Stale local observation IDs.
        """
        self._database_connection.execute(
            """
            DELETE FROM observation_photos AS photos
            WHERE photos.project_alias = %s
                AND photos.observation_id = ANY(%s)
            """,
            (project_alias, stale_observation_ids),
        )

    def _delete_orphan_observers(self):
        """Delete observers not referenced by any local observation."""
        self._database_connection.execute(
            """
            DELETE FROM observers AS observer_rows
            WHERE NOT EXISTS (
                SELECT 1
                FROM observations AS observation_rows
                WHERE observation_rows.observer_id = observer_rows.observer_id
            )
            """
        )

    def _delete_orphan_taxa(self):
        """Delete taxa not referenced by observations or their taxon lineages."""
        self._database_connection.execute(
            """
            DELETE FROM taxa AS taxon_rows
            WHERE NOT EXISTS (
                SELECT 1
                FROM observations AS observation_rows
                WHERE observation_rows.taxon_id = taxon_rows.taxon_id
            )
                AND NOT EXISTS (
                    SELECT 1
                    FROM taxa AS observed_taxa
                    WHERE observed_taxa.ancestor_ids @> jsonb_build_array(taxon_rows.taxon_id)
                        AND EXISTS (
                            SELECT 1
                            FROM observations AS observation_rows
                            WHERE observation_rows.taxon_id = observed_taxa.taxon_id
                        )
                )
            """
        )
