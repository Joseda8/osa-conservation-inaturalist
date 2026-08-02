"""Taxon field selections for iNaturalist API requests.

@file taxon_fields.py
@brief Defines fields required to populate complete taxonomy lineages.
"""


# Taxon fields represented by the PostgreSQL taxa table.
TAXON_ENRICHMENT_FIELDS = {
    "id": True,
    "name": True,
    "preferred_common_name": True,
    "rank": True,
    "rank_level": True,
    "parent_id": True,
    "ancestor_ids": True,
    "iconic_taxon_id": True,
    "iconic_taxon_name": True,
    "is_active": True,
    "native": True,
    "introduced": True,
    "endemic": True,
    "threatened": True,
    "extinct": True,
}
