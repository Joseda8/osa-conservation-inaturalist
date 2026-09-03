"""Observation field selections for iNaturalist API requests.

@file observation_fields.py
@brief Defines targeted observation fields for analysis-oriented downloads.
"""


# Observation fields needed for biodiversity baseline and iNaturalist research summaries.
# iNaturalist observation timestamp field, which is null when the observer did not supply a time.
TIME_OBSERVED_AT_FIELD_NAME = "time_observed_at"


OBSERVATION_ANALYSIS_FIELDS = {
    "id": True,
    "quality_grade": True,
    "species_guess": True,
    "observed_on": True,
    TIME_OBSERVED_AT_FIELD_NAME: True,
    "created_at": True,
    "updated_at": True,
    "geojson": True,
    "location": True,
    "place_guess": True,
    "positional_accuracy": True,
    "public_positional_accuracy": True,
    "geoprivacy": True,
    "taxon_geoprivacy": True,
    "obscured": True,
    "mappable": True,
    "captive": True,
    "project_ids": True,
    "project_ids_with_curator_id": True,
    "project_ids_without_curator_id": True,
    "identifications_count": True,
    "num_identification_agreements": True,
    "num_identification_disagreements": True,
    "taxon": {
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
    },
    "user": {
        "id": True,
        "login": True,
        "name": True,
        "observations_count": True,
        "species_count": True,
    },
    "photos": {
        "id": True,
        "url": True,
        "license_code": True,
        "attribution": True,
        "hidden": True,
        "original_dimensions": True,
    },
}
