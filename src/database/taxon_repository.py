"""Taxon database operations.

@file taxon_repository.py
@brief Stores taxon metadata and finds missing taxonomy lineage nodes.
"""

from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb

from .constants import DELETE_TAXON_CONSERVATION_STATUSES_QUERY_PATH, MARK_TAXON_CONSERVATION_STATUSES_LOADED_QUERY_PATH, SELECT_ALL_TAXON_IDS_QUERY_PATH, SELECT_MISSING_LINEAGE_TAXON_IDS_QUERY_PATH, SELECT_TAXON_IDS_MISSING_CONSERVATION_STATUSES_QUERY_PATH, UPSERT_TAXON_CONSERVATION_STATUS_QUERY_PATH, UPSERT_TAXON_QUERY_PATH
from .query_loader import load_sql_query

class TaxonRepository:
    """Stores and queries iNaturalist taxa.

    @param database_connection Open PostgreSQL connection.
    """

    def __init__(self, database_connection: Connection):
        """Create a taxon repository.

        @param database_connection Open PostgreSQL connection.
        """
        self._database_connection = database_connection

    def get_all_taxon_ids(self) -> list[int]:
        """Get every taxon ID currently stored.

        @return Sorted taxon IDs.
        """
        taxon_rows = self._database_connection.execute(load_sql_query(SELECT_ALL_TAXON_IDS_QUERY_PATH)).fetchall()
        return [int(taxon_row[0]) for taxon_row in taxon_rows]

    def get_missing_lineage_taxon_ids(self) -> list[int]:
        """Get ancestor IDs referenced by taxa but absent from the taxa table.

        @return Sorted missing ancestor taxon IDs.
        """
        missing_taxon_rows = self._database_connection.execute(load_sql_query(SELECT_MISSING_LINEAGE_TAXON_IDS_QUERY_PATH)).fetchall()
        return [int(missing_taxon_row[0]) for missing_taxon_row in missing_taxon_rows]

    def get_taxon_ids_missing_conservation_statuses(self) -> list[int]:
        """Get taxon IDs that have not yet been enriched with iNaturalist statuses.

        @return Sorted taxon IDs.
        """
        taxon_rows = self._database_connection.execute(load_sql_query(SELECT_TAXON_IDS_MISSING_CONSERVATION_STATUSES_QUERY_PATH)).fetchall()
        return [int(taxon_row[0]) for taxon_row in taxon_rows]

    def upsert_taxa(self, taxon_json_rows: list[dict[str, Any]], loaded_from: str, include_conservation_statuses: bool = False) -> int:
        """Insert or update taxon metadata.

        @param taxon_json_rows Taxon API response rows.
        @param loaded_from Source that supplied the taxon rows.
        @param include_conservation_statuses Whether to replace statuses from taxonomy enrichment.
        @return Number of processed taxon rows.
        """
        for taxon_json in taxon_json_rows:
            self._database_connection.execute(
                load_sql_query(UPSERT_TAXON_QUERY_PATH),
                (
                    taxon_json["id"],
                    taxon_json.get("name"),
                    taxon_json.get("preferred_common_name"),
                    taxon_json.get("rank"),
                    taxon_json.get("rank_level"),
                    taxon_json.get("parent_id"),
                    Jsonb(taxon_json.get("ancestor_ids")),
                    taxon_json.get("iconic_taxon_id"),
                    taxon_json.get("iconic_taxon_name"),
                    taxon_json.get("is_active"),
                    taxon_json.get("native"),
                    taxon_json.get("introduced"),
                    taxon_json.get("endemic"),
                    taxon_json.get("threatened"),
                    taxon_json.get("extinct"),
                    loaded_from,
                ),
            )
            if include_conservation_statuses:
                self._replace_conservation_statuses(taxon_json, loaded_from)
        return len(taxon_json_rows)

    def _replace_conservation_statuses(self, taxon_json: dict[str, Any], loaded_from: str):
        """Replace one taxon's statuses with the iNaturalist response without interpretation.

        @param taxon_json iNaturalist taxon payload.
        @param loaded_from Source that supplied the taxon payload.
        """
        taxon_id = taxon_json["id"]
        self._database_connection.execute(load_sql_query(DELETE_TAXON_CONSERVATION_STATUSES_QUERY_PATH), (taxon_id,))
        conservation_statuses = [taxon_json.get("conservation_status"), *(taxon_json.get("conservation_statuses") or [])]
        stored_status_ids = set()
        for conservation_status in conservation_statuses:
            if not isinstance(conservation_status, dict) or conservation_status.get("id") is None:
                continue
            conservation_status_id = conservation_status["id"]
            if conservation_status_id in stored_status_ids:
                continue
            stored_status_ids.add(conservation_status_id)
            self._database_connection.execute(
                load_sql_query(UPSERT_TAXON_CONSERVATION_STATUS_QUERY_PATH),
                (
                    conservation_status_id,
                    taxon_id,
                    conservation_status.get("place_id"),
                    conservation_status.get("source_id"),
                    conservation_status.get("user_id"),
                    conservation_status.get("authority"),
                    conservation_status.get("status"),
                    conservation_status.get("status_name"),
                    conservation_status.get("geoprivacy"),
                    conservation_status.get("iucn"),
                    loaded_from,
                ),
            )
        self._database_connection.execute(load_sql_query(MARK_TAXON_CONSERVATION_STATUSES_LOADED_QUERY_PATH), (taxon_id,))
