"""Raw data database load pipeline step.

@file load_raw_data_to_database_step.py
@brief Loads raw iNaturalist JSON files into PostgreSQL.
"""

from database import RawDataLoader, open_database_connection
from pipeline.pipeline_context import PipelineContext


class LoadRawDataToDatabaseStep:
    """Pipeline step that loads downloaded raw data into PostgreSQL."""

    name = "load-raw-data-to-db"

    def run(self, pipeline_context: PipelineContext):
        """Load raw JSON data into PostgreSQL.

        @param pipeline_context Shared pipeline state.
        """
        with open_database_connection() as database_connection:
            RawDataLoader(database_connection, pipeline_context.project_configs).load()
