"""Project observation reconciliation pipeline step.

@file reconcile_project_observations_step.py
@brief Deletes local observations that no longer belong to configured projects.
"""

from database import ProjectObservationReconciler, open_database_connection
from pipeline.pipeline_context import PipelineContext


class ReconcileProjectObservationsStep:
    """Pipeline step that reconciles project membership against iNaturalist."""

    name = "reconcile-project-observations"

    def run(self, pipeline_context: PipelineContext):
        """Reconcile local project observations against current iNaturalist IDs.

        @param pipeline_context Shared pipeline state.
        """
        inaturalist_client = pipeline_context.get_inaturalist_client()
        with open_database_connection() as database_connection:
            project_observation_reconciler = ProjectObservationReconciler(database_connection)
            for project_config in pipeline_context.project_configs:
                local_observation_ids = project_observation_reconciler.get_local_observation_ids(
                    project_config
                )
                stale_observation_ids = inaturalist_client.get_stale_observation_ids(
                    project_config,
                    observation_ids=local_observation_ids,
                    failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
                )
                project_observation_reconciler.delete_stale_observations(
                    project_config,
                    stale_observation_ids,
                )
