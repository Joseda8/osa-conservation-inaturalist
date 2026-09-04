"""Observation field selections for iNaturalist API requests.

@file observation_fields.py
@brief Defines targeted observation fields for analysis-oriented downloads.
"""

from .taxon_fields import TAXON_OBSERVATION_FIELDS


# Observation fields needed for biodiversity baseline and iNaturalist research summaries.
OBSERVATION_ANALYSIS_FIELDS = {
    "id": True,
    "quality_grade": True,
    "species_guess": True,
    "observed_on": True,
    "time_observed_at": True,
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
    "taxon": TAXON_OBSERVATION_FIELDS,
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
