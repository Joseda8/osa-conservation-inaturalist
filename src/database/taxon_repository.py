"""Taxon database operations.

@file taxon_repository.py
@brief Stores taxon metadata and finds missing taxonomy lineage nodes.
"""

from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb


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
        taxon_rows = self._database_connection.execute(
            """
            SELECT taxon_id
            FROM taxa
            ORDER BY taxon_id
            """
        ).fetchall()
        return [int(taxon_row[0]) for taxon_row in taxon_rows]

    def get_missing_lineage_taxon_ids(self) -> list[int]:
        """Get ancestor IDs referenced by taxa but absent from the taxa table.

        @return Sorted missing ancestor taxon IDs.
        """
        missing_taxon_rows = self._database_connection.execute(
            """
            WITH referenced_taxon_ids AS (
                SELECT DISTINCT ancestor_id.value::BIGINT AS taxon_id
                FROM taxa AS source_taxa
                CROSS JOIN LATERAL jsonb_array_elements_text(
                    COALESCE(source_taxa.ancestor_ids, '[]'::JSONB)
                ) AS ancestor_id(value)
            )
            SELECT referenced_taxon_ids.taxon_id
            FROM referenced_taxon_ids
            LEFT JOIN taxa AS stored_taxa
                ON stored_taxa.taxon_id = referenced_taxon_ids.taxon_id
            WHERE stored_taxa.taxon_id IS NULL
            ORDER BY referenced_taxon_ids.taxon_id
            """
        ).fetchall()
        return [int(missing_taxon_row[0]) for missing_taxon_row in missing_taxon_rows]

    def upsert_taxa(self, taxon_json_rows: list[dict[str, Any]], loaded_from: str) -> int:
        """Insert or update taxon metadata.

        @param taxon_json_rows Taxon API response rows.
        @param loaded_from Source that supplied the taxon rows.
        @return Number of processed taxon rows.
        """
        for taxon_json in taxon_json_rows:
            self._database_connection.execute(
                """
                INSERT INTO taxa (
                    taxon_id,
                    scientific_name,
                    common_name,
                    rank,
                    rank_level,
                    parent_id,
                    ancestor_ids,
                    ancestry,
                    iconic_taxon_id,
                    iconic_taxon_name,
                    is_active,
                    native,
                    introduced,
                    endemic,
                    threatened,
                    extinct,
                    loaded_from,
                    loaded_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (taxon_id) DO UPDATE SET
                    scientific_name = EXCLUDED.scientific_name,
                    common_name = EXCLUDED.common_name,
                    rank = EXCLUDED.rank,
                    rank_level = EXCLUDED.rank_level,
                    parent_id = EXCLUDED.parent_id,
                    ancestor_ids = EXCLUDED.ancestor_ids,
                    ancestry = EXCLUDED.ancestry,
                    iconic_taxon_id = EXCLUDED.iconic_taxon_id,
                    iconic_taxon_name = EXCLUDED.iconic_taxon_name,
                    is_active = EXCLUDED.is_active,
                    native = EXCLUDED.native,
                    introduced = EXCLUDED.introduced,
                    endemic = EXCLUDED.endemic,
                    threatened = EXCLUDED.threatened,
                    extinct = EXCLUDED.extinct,
                    loaded_from = EXCLUDED.loaded_from,
                    loaded_at = now()
                """,
                (
                    taxon_json["id"],
                    taxon_json.get("name"),
                    taxon_json.get("preferred_common_name"),
                    taxon_json.get("rank"),
                    taxon_json.get("rank_level"),
                    taxon_json.get("parent_id"),
                    Jsonb(taxon_json.get("ancestor_ids")),
                    taxon_json.get("ancestry"),
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
        return len(taxon_json_rows)
