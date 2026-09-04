"""Taxon field selections for iNaturalist API requests.

@file taxon_fields.py
@brief Defines fields required to populate complete taxonomy lineages.
"""


# Taxon fields stored with each downloaded observation.
TAXON_OBSERVATION_FIELDS = {
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

# Additional fields requested only by the taxonomy enrichment step.
TAXON_ENRICHMENT_FIELDS = {
    **TAXON_OBSERVATION_FIELDS,
    "conservation_status": {
        "id": True,
        "source_id": True,
        "user_id": True,
        "authority": True,
        "place_id": True,
        "status": True,
        "status_name": True,
        "geoprivacy": True,
        "iucn": True,
    },
    "conservation_statuses": {
        "id": True,
        "source_id": True,
        "user_id": True,
        "authority": True,
        "place_id": True,
        "status": True,
        "status_name": True,
        "geoprivacy": True,
        "iucn": True,
    },
}
