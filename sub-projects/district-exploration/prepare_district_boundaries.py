"""Prepare Costa Rica district boundaries for local exploration.

@file prepare_district_boundaries.py
@brief Downloads official INEC boundaries and creates CSV and GeoJSON files.
"""

from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

import geopandas
from utils import LOGGER


# Folder containing this district exploration sub-project.
SUB_PROJECT_DIR = Path(__file__).resolve().parent

# Local folder for downloaded and converted district data.
DATA_DIR = SUB_PROJECT_DIR / "data"

# Official INEC 2024 district boundary archive.
DISTRICT_ARCHIVE_URL = (
    "https://admin.inec.cr/sites/default/files/2025-01/"
    "Unidad%20Geoestad%C3%ADstica%20Distrital%202024.zip"
)

# Local path for the downloaded INEC archive.
DISTRICT_ARCHIVE_PATH = DATA_DIR / "source" / "inec_districts_2024.zip"

# Local folder for extracted INEC source files.
DISTRICT_SOURCE_DIR = DATA_DIR / "source" / "inec_districts_2024"

# Shapefile contained in the official INEC archive.
DISTRICT_SHAPEFILE_PATH = (
    DISTRICT_SOURCE_DIR / "Unidad Geoestadística Distrital 2024.shp"
)

# CSV containing standardized district metadata and WKT polygons.
DISTRICT_CSV_PATH = DATA_DIR / "district_boundaries.csv"

# GeoJSON used for local point-in-polygon matching.
DISTRICT_GEOJSON_PATH = DATA_DIR / "district_boundaries.geojson"

# INEC source columns renamed for the exploration output.
DISTRICT_COLUMN_NAMES = {
    "NOMB_UGEP": "province_name",
    "NOMB_UGEC": "canton_name",
    "NOMB_UGED": "district_name",
    "COD_UGED": "district_code",
    "AREA_M2": "area_square_meters",
    "FECHA_ACTU": "source_updated_on",
}


def _download_archive():
    """Download the official INEC boundary archive when absent."""
    if DISTRICT_ARCHIVE_PATH.exists():
        LOGGER.info("Using existing INEC archive: %s", DISTRICT_ARCHIVE_PATH)
        return

    DISTRICT_ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Downloading INEC district boundaries")
    download_request = Request(
        DISTRICT_ARCHIVE_URL,
        headers={"User-Agent": "osa-inaturalist-district-exploration"},
    )
    with urlopen(download_request) as download_response:
        DISTRICT_ARCHIVE_PATH.write_bytes(download_response.read())
    LOGGER.info("Stored INEC archive: %s", DISTRICT_ARCHIVE_PATH)


def _extract_archive():
    """Extract the official district shapefile when absent."""
    if DISTRICT_SHAPEFILE_PATH.exists():
        LOGGER.info("Using existing INEC shapefile: %s", DISTRICT_SHAPEFILE_PATH)
        return

    DISTRICT_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(DISTRICT_ARCHIVE_PATH) as district_archive:
        district_archive.extractall(DISTRICT_SOURCE_DIR)
    LOGGER.info("Extracted INEC district boundaries: %s", DISTRICT_SOURCE_DIR)


def _load_standardized_boundaries() -> geopandas.GeoDataFrame:
    """Load and standardize the official district boundaries.

    @return District boundaries using project column names and WGS84 coordinates.
    """
    source_boundaries = geopandas.read_file(
        DISTRICT_SHAPEFILE_PATH,
        encoding="UTF-8",
    )
    missing_columns = sorted(set(DISTRICT_COLUMN_NAMES) - set(source_boundaries.columns))
    if missing_columns:
        raise ValueError(
            "INEC district file is missing expected columns: "
            + ", ".join(missing_columns)
        )
    if source_boundaries.crs is None:
        raise ValueError("INEC district file does not declare a coordinate system")

    district_boundaries = source_boundaries.rename(columns=DISTRICT_COLUMN_NAMES)
    district_boundaries = district_boundaries[
        [*DISTRICT_COLUMN_NAMES.values(), "geometry"]
    ].to_crs("EPSG:4326")
    district_boundaries["district_code"] = (
        district_boundaries["district_code"].astype(str).str.strip()
    )
    return district_boundaries


def _write_boundary_outputs(district_boundaries: geopandas.GeoDataFrame):
    """Write district boundaries as CSV and GeoJSON.

    @param district_boundaries Standardized district polygons.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    district_csv = district_boundaries.drop(columns="geometry").copy()
    district_csv["geometry_wkt"] = district_boundaries.geometry.to_wkt()
    district_csv.to_csv(DISTRICT_CSV_PATH, index=False, encoding="UTF-8")
    district_boundaries.to_file(DISTRICT_GEOJSON_PATH, driver="GeoJSON")
    LOGGER.info("Stored district boundary CSV: %s", DISTRICT_CSV_PATH)
    LOGGER.info("Stored district boundary GeoJSON: %s", DISTRICT_GEOJSON_PATH)


def main():
    """Download, standardize, and store Costa Rica district boundaries."""
    _download_archive()
    _extract_archive()
    district_boundaries = _load_standardized_boundaries()
    _write_boundary_outputs(district_boundaries)
    LOGGER.info("Prepared %s district polygons", len(district_boundaries))


if __name__ == "__main__":
    main()
