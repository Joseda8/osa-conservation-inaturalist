"""Taxonomy enrichment pipeline step.

@file enrich_taxonomy_step.py
@brief Completes taxon lineages with metadata from iNaturalist.
"""

from psycopg import Connection
from utils import LOGGER

from database import TaxonRepository, open_database_connection
from inaturalist_client.constants import TAXON_ENRICHMENT_BATCH_SIZE
from pipeline.pipeline_context import PipelineContext


# Source reference used for taxa fetched by the enrichment step.
TAXON_API_SOURCE = "iNaturalist API v2 /taxa"


class EnrichTaxonomyStep:
    """Pipeline step that completes stored taxonomy lineages."""

    name = "enrich-taxonomy"

    def run(self, pipeline_context: PipelineContext):
        """Enrich stored taxa with every referenced lineage node.

        @param pipeline_context Shared pipeline state.
        """
        LOGGER.info("Starting taxonomy enrichment in %s mode", pipeline_context.taxonomy_mode)
        with open_database_connection() as database_connection:
            taxon_repository = TaxonRepository(database_connection)
            if pipeline_context.taxonomy_mode == "full":
                with database_connection.transaction():
                    stored_taxon_ids = taxon_repository.get_all_taxon_ids()
                LOGGER.info("Refreshing %s stored taxa", len(stored_taxon_ids))
                self._enrich_taxon_ids(
                    stored_taxon_ids,
                    database_connection,
                    taxon_repository,
                    pipeline_context,
                    force_refresh=True,
                )

            while True:
                with database_connection.transaction():
                    missing_taxon_ids = taxon_repository.get_missing_lineage_taxon_ids()
                if not missing_taxon_ids:
                    break

                LOGGER.info("Found %s missing taxonomy lineage nodes", len(missing_taxon_ids))
                self._enrich_taxon_ids(
                    missing_taxon_ids,
                    database_connection,
                    taxon_repository,
                    pipeline_context,
                    force_refresh=False,
                )

            with database_connection.transaction():
                stored_taxon_count = len(taxon_repository.get_all_taxon_ids())
            LOGGER.info("Taxonomy enrichment complete with %s stored taxa", stored_taxon_count)

    def _enrich_taxon_ids(
        self,
        taxon_ids: list[int],
        database_connection: Connection,
        taxon_repository: TaxonRepository,
        pipeline_context: PipelineContext,
        force_refresh: bool,
    ):
        """Fetch and store taxon IDs in fixed-size batches.

        @param taxon_ids Taxon IDs to enrich.
        @param database_connection Open PostgreSQL connection.
        @param taxon_repository Taxon persistence helper.
        @param pipeline_context Shared pipeline state.
        @param force_refresh Whether to bypass cached API responses.
        """
        if not taxon_ids:
            return

        total_batches = (
            len(taxon_ids) + TAXON_ENRICHMENT_BATCH_SIZE - 1
        ) // TAXON_ENRICHMENT_BATCH_SIZE
        for batch_start in range(0, len(taxon_ids), TAXON_ENRICHMENT_BATCH_SIZE):
            batch_number = (batch_start // TAXON_ENRICHMENT_BATCH_SIZE) + 1
            taxon_id_batch = taxon_ids[
                batch_start : batch_start + TAXON_ENRICHMENT_BATCH_SIZE
            ]
            LOGGER.info("Requesting taxonomy batch %s/%s with %s taxa", batch_number, total_batches, len(taxon_id_batch))
            taxon_rows = pipeline_context.get_inaturalist_client().get_taxa(
                taxon_id_batch,
                request_cooldown_seconds=pipeline_context.request_cooldown_seconds,
                failure_cooldown_seconds=pipeline_context.failure_cooldown_seconds,
                force_refresh=force_refresh,
            )
            with database_connection.transaction():
                stored_taxon_count = taxon_repository.upsert_taxa(
                    taxon_rows,
                    TAXON_API_SOURCE,
                )
            LOGGER.info("Stored %s taxa from taxonomy batch %s/%s", stored_taxon_count, batch_number, total_batches)
