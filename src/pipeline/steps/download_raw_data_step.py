"""Raw data download pipeline step.

@file download_raw_data_step.py
@brief Downloads raw iNaturalist project data.
"""

from pipeline.pipeline_context import PipelineContext


class DownloadRawDataStep:
    """Pipeline step that downloads raw iNaturalist project data."""

    name = "download-raw-data"

    def run(self, pipeline_context: PipelineContext):
        """Download raw observation pages for configured projects.

        @param pipeline_context Shared pipeline state.
        """
        for project_config in pipeline_context.project_configs:
            project_summary = pipeline_context.inaturalist_client.download_project_observations(
                project_config,
                per_page=pipeline_context.per_page,
                request_cooldown_seconds=pipeline_context.request_cooldown_seconds,
                failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
            )
            pipeline_context.download_summaries.append(project_summary)
