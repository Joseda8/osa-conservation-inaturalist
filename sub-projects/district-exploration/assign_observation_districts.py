"""Assign local observations to Costa Rica districts.

@file assign_observation_districts.py
@brief Reads PostgreSQL observations and writes a district-enriched CSV.
"""

from pathlib import Path

import geopandas
import pandas
from database import open_database_connection
from utils import LOGGER


# Folder containing this district exploration sub-project.
SUB_PROJECT_DIR = Path(__file__).resolve().parent

# GeoJSON created by prepare_district_boundaries.py.
DISTRICT_GEOJSON_PATH = SUB_PROJECT_DIR / "data" / "district_boundaries.geojson"

# Local folder for generated exploration results.
OUTPUT_DIR = SUB_PROJECT_DIR / "outputs"

# CSV mapping each observation's location values to a district.
OBSERVATION_DISTRICTS_PATH = OUTPUT_DIR / "observation_districts.csv"

# Observation columns exported from the shared PostgreSQL database.
OBSERVATION_COLUMNS = [
    "observation_id",
    "observed_on",
    "observed_year",
    "observed_month",
    "observed_day",
    "location",
    "longitude",
    "latitude",
]

# Read-only query for observation dates and locations used by the exploration.
OBSERVATION_QUERY = """
    SELECT DISTINCT ON (observation_id)
        observation_id,
        observed_on,
        observed_year,
        observed_month,
        observed_day,
        location,
        longitude,
        latitude
    FROM observations
    ORDER BY
        observation_id,
        updated_at DESC NULLS LAST,
        loaded_at DESC
"""

# District columns added to the observation output.
DISTRICT_COLUMNS = [
    "district_code",
    "district_name",
]


def _load_observations() -> pandas.DataFrame:
    """Read observations from PostgreSQL without modifying the database.

    @return Observation rows as a data frame.
    """
    LOGGER.info("Reading observations from PostgreSQL")
    with open_database_connection() as database_connection:
        observation_rows = database_connection.execute(OBSERVATION_QUERY).fetchall()
    observations = pandas.DataFrame(observation_rows, columns=OBSERVATION_COLUMNS)
    LOGGER.info("Loaded %s observations", len(observations))
    return observations


def _load_district_boundaries() -> geopandas.GeoDataFrame:
    """Read prepared district polygons.

    @return District polygons in WGS84 coordinates.
    """
    if not DISTRICT_GEOJSON_PATH.exists():
        raise FileNotFoundError(
            "District boundaries are missing. Run prepare_district_boundaries.py first."
        )
    district_boundaries = geopandas.read_file(DISTRICT_GEOJSON_PATH)
    return district_boundaries[[*DISTRICT_COLUMNS, "geometry"]].to_crs("EPSG:4326")


def _match_observations_to_districts(
    observations: pandas.DataFrame,
    district_boundaries: geopandas.GeoDataFrame,
) -> pandas.DataFrame:
    """Match public observation coordinates to district polygons.

    @param observations Database observation rows.
    @param district_boundaries Costa Rica district polygons.
    @return Observation IDs and location values with matched district columns.
    """
    located_observations = observations.dropna(subset=["longitude", "latitude"]).copy()
    observation_points = geopandas.GeoDataFrame(
        located_observations,
        geometry=geopandas.points_from_xy(
            located_observations["longitude"],
            located_observations["latitude"],
        ),
        crs="EPSG:4326",
    )
    matched_observations = geopandas.sjoin(
        observation_points,
        district_boundaries,
        how="left",
        predicate="within",
    )
    duplicate_matches = matched_observations.duplicated(
        subset=["observation_id"],
        keep=False,
    )
    if duplicate_matches.any():
        raise ValueError(
            f"District polygons produced {int(duplicate_matches.sum())} duplicate matches"
        )

    matched_columns = ["observation_id", *DISTRICT_COLUMNS]
    observation_districts = observations.merge(
        matched_observations[matched_columns],
        on="observation_id",
        how="left",
    )
    return observation_districts.rename(
        columns={
            "district_code": "matched_district_code",
            "district_name": "matched_district",
        }
    )[
        [
            *OBSERVATION_COLUMNS,
            "matched_district_code",
            "matched_district",
        ]
    ]


def main():
    """Create the local observation-to-district exploration CSV."""
    observations = _load_observations()
    district_boundaries = _load_district_boundaries()
    observation_districts = _match_observations_to_districts(
        observations,
        district_boundaries,
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    observation_districts.to_csv(
        OBSERVATION_DISTRICTS_PATH,
        index=False,
        encoding="UTF-8",
    )
    matched_count = int(observation_districts["matched_district_code"].notna().sum())
    LOGGER.info(
        "Stored %s observations with %s district matches: %s",
        len(observation_districts),
        matched_count,
        OBSERVATION_DISTRICTS_PATH,
    )


if __name__ == "__main__":
    main()
