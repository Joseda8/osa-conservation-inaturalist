"""Generate yearly district observation heat maps as KML files.

@file generate_yearly_district_heatmaps.py
@brief Creates one district-level observation heat map for each observed year.
"""

from pathlib import Path
from xml.etree import ElementTree

import geopandas
import pandas
from utils import LOGGER


# Folder containing this district exploration sub-project.
SUB_PROJECT_DIR = Path(__file__).resolve().parent

# CSV created by assign_observation_districts.py.
OBSERVATION_DISTRICTS_PATH = (
    SUB_PROJECT_DIR / "outputs" / "observation_districts.csv"
)

# GeoJSON created by prepare_district_boundaries.py.
DISTRICT_GEOJSON_PATH = SUB_PROJECT_DIR / "data" / "district_boundaries.geojson"

# Folder containing one generated KML heat map per year.
HEATMAP_OUTPUT_DIR = SUB_PROJECT_DIR / "outputs" / "yearly_heatmaps"

# XML namespace used by KML documents.
KML_NAMESPACE = "http://www.opengis.net/kml/2.2"

# Stable observation-count bands shared by every yearly map.
OBSERVATION_COUNT_STYLES = [
    (0, "zero", "00ffffff"),
    (1, "very-low", "ccb2ffff"),
    (10, "low", "cc5cccfe"),
    (50, "medium", "cc3c8dfd"),
    (200, "high", "cc203bf0"),
    (1000, "very-high", "cc2600bd"),
]


def _qualified_name(element_name: str) -> str:
    """Build a KML-qualified XML element name.

    @param element_name Local XML element name.
    @return Element name qualified with the KML namespace.
    """
    return f"{{{KML_NAMESPACE}}}{element_name}"


def _add_styles(document: ElementTree.Element):
    """Add shared observation-count styles to a KML document.

    @param document KML document element.
    """
    for _, style_name, fill_color in OBSERVATION_COUNT_STYLES:
        style = ElementTree.SubElement(
            document,
            _qualified_name("Style"),
            {"id": style_name},
        )
        line_style = ElementTree.SubElement(style, _qualified_name("LineStyle"))
        ElementTree.SubElement(line_style, _qualified_name("color")).text = (
            "cc666666"
        )
        ElementTree.SubElement(line_style, _qualified_name("width")).text = "1"
        polygon_style = ElementTree.SubElement(style, _qualified_name("PolyStyle"))
        ElementTree.SubElement(polygon_style, _qualified_name("color")).text = (
            fill_color
        )
        ElementTree.SubElement(polygon_style, _qualified_name("fill")).text = "1"
        ElementTree.SubElement(polygon_style, _qualified_name("outline")).text = "1"


def _get_style_name(observation_count: int) -> str:
    """Select the stable style band for an observation count.

    @param observation_count Number of observations in a district and year.
    @return KML style identifier.
    """
    selected_style_name = OBSERVATION_COUNT_STYLES[0][1]
    for minimum_count, style_name, _ in OBSERVATION_COUNT_STYLES:
        if observation_count < minimum_count:
            break
        selected_style_name = style_name
    return selected_style_name


def _format_coordinates(coordinates) -> str:
    """Convert polygon coordinates to the KML coordinate syntax.

    @param coordinates Sequence of longitude and latitude pairs.
    @return Space-separated KML coordinates.
    """
    return " ".join(
        f"{longitude:.8f},{latitude:.8f},0"
        for longitude, latitude, *_ in coordinates
    )


def _add_polygon(parent: ElementTree.Element, polygon):
    """Add one polygon geometry to a KML element.

    @param parent Parent placemark or multi-geometry element.
    @param polygon Shapely polygon to serialize.
    """
    polygon_element = ElementTree.SubElement(parent, _qualified_name("Polygon"))
    ElementTree.SubElement(polygon_element, _qualified_name("tessellate")).text = "1"
    outer_boundary = ElementTree.SubElement(
        polygon_element,
        _qualified_name("outerBoundaryIs"),
    )
    outer_ring = ElementTree.SubElement(
        outer_boundary,
        _qualified_name("LinearRing"),
    )
    ElementTree.SubElement(outer_ring, _qualified_name("coordinates")).text = (
        _format_coordinates(polygon.exterior.coords)
    )

    for interior_ring in polygon.interiors:
        inner_boundary = ElementTree.SubElement(
            polygon_element,
            _qualified_name("innerBoundaryIs"),
        )
        inner_ring = ElementTree.SubElement(
            inner_boundary,
            _qualified_name("LinearRing"),
        )
        ElementTree.SubElement(inner_ring, _qualified_name("coordinates")).text = (
            _format_coordinates(interior_ring.coords)
        )


def _add_geometry(placemark: ElementTree.Element, geometry):
    """Add polygon or multipolygon geometry to a KML placemark.

    @param placemark KML placemark element.
    @param geometry Shapely district geometry.
    """
    if geometry.geom_type == "Polygon":
        _add_polygon(placemark, geometry)
        return
    if geometry.geom_type == "MultiPolygon":
        multi_geometry = ElementTree.SubElement(
            placemark,
            _qualified_name("MultiGeometry"),
        )
        for polygon in geometry.geoms:
            _add_polygon(multi_geometry, polygon)
        return
    raise ValueError(f"Unsupported district geometry: {geometry.geom_type}")


def _load_observation_counts() -> tuple[pandas.DataFrame, pandas.Series]:
    """Load annual district counts and each district's first observation year.

    @return Annual counts and first observation year indexed by district code.
    """
    observations = pandas.read_csv(
        OBSERVATION_DISTRICTS_PATH,
        dtype={"matched_district_code": "string"},
        usecols=["observed_year", "matched_district_code"],
    ).dropna(subset=["observed_year", "matched_district_code"])
    observations["observed_year"] = observations["observed_year"].astype(int)
    annual_counts = (
        observations.groupby(["observed_year", "matched_district_code"])
        .size()
        .rename("observation_count")
        .reset_index()
    )
    first_observation_years = observations.groupby("matched_district_code")[
        "observed_year"
    ].min()
    return annual_counts, first_observation_years


def _load_boundaries() -> geopandas.GeoDataFrame:
    """Load district polygons used by the yearly KML files.

    @return District boundaries in WGS84 coordinates.
    """
    district_boundaries = geopandas.read_file(DISTRICT_GEOJSON_PATH).to_crs(
        "EPSG:4326"
    )
    district_boundaries["district_code"] = district_boundaries[
        "district_code"
    ].astype(str)
    return district_boundaries


def _write_yearly_heatmap(
    observed_year: int,
    district_boundaries: geopandas.GeoDataFrame,
    annual_counts: pandas.DataFrame,
    first_observation_years: pandas.Series,
):
    """Write one district observation heat map for an observed year.

    @param observed_year Year represented by the KML file.
    @param district_boundaries Costa Rica district polygons.
    @param annual_counts Observation counts grouped by year and district.
    @param first_observation_years First observed year indexed by district code.
    """
    year_counts = annual_counts[annual_counts["observed_year"] == observed_year]
    yearly_boundaries = district_boundaries.merge(
        year_counts[["matched_district_code", "observation_count"]],
        left_on="district_code",
        right_on="matched_district_code",
        how="left",
    )
    yearly_boundaries["observation_count"] = (
        yearly_boundaries["observation_count"].fillna(0).astype(int)
    )

    ElementTree.register_namespace("", KML_NAMESPACE)
    kml = ElementTree.Element(_qualified_name("kml"))
    document = ElementTree.SubElement(kml, _qualified_name("Document"))
    ElementTree.SubElement(document, _qualified_name("name")).text = (
        f"Costa Rica district observations - {observed_year}"
    )
    _add_styles(document)

    for district in yearly_boundaries.itertuples(index=False):
        observation_count = int(district.observation_count)
        area_square_kilometers = district.area_square_meters / 1_000_000
        observation_density = observation_count / area_square_kilometers
        first_observation_year = first_observation_years.get(district.district_code)
        first_year_text = (
            str(int(first_observation_year))
            if pandas.notna(first_observation_year)
            else "No observations"
        )

        placemark = ElementTree.SubElement(document, _qualified_name("Placemark"))
        ElementTree.SubElement(placemark, _qualified_name("name")).text = (
            district.district_name
        )
        ElementTree.SubElement(placemark, _qualified_name("styleUrl")).text = (
            f"#{_get_style_name(observation_count)}"
        )
        ElementTree.SubElement(placemark, _qualified_name("description")).text = (
            f"District: {district.district_name}\n"
            f"Canton: {district.canton_name}\n"
            f"Province: {district.province_name}\n"
            f"Observations in {observed_year}: {observation_count}\n"
            f"Observations per km²: {observation_density:.2f}\n"
            f"First observation year: {first_year_text}"
        )
        _add_geometry(placemark, district.geometry)

    HEATMAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    heatmap_path = HEATMAP_OUTPUT_DIR / f"district_observations_{observed_year}.kml"
    ElementTree.indent(kml, space="  ")
    ElementTree.ElementTree(kml).write(
        heatmap_path,
        encoding="UTF-8",
        xml_declaration=True,
    )
    LOGGER.info("Stored yearly district heat map: %s", heatmap_path)


def main():
    """Generate one KML district observation heat map per observed year."""
    if not OBSERVATION_DISTRICTS_PATH.exists():
        raise FileNotFoundError(
            "Observation districts are missing. Run "
            "assign_observation_districts.py first."
        )
    if not DISTRICT_GEOJSON_PATH.exists():
        raise FileNotFoundError(
            "District boundaries are missing. Run prepare_district_boundaries.py first."
        )

    annual_counts, first_observation_years = _load_observation_counts()
    district_boundaries = _load_boundaries()
    observed_years = sorted(annual_counts["observed_year"].unique())
    LOGGER.info("Generating district heat maps for %s years", len(observed_years))
    for observed_year in observed_years:
        _write_yearly_heatmap(
            int(observed_year),
            district_boundaries,
            annual_counts,
            first_observation_years,
        )
    LOGGER.info("Completed %s yearly district heat maps", len(observed_years))


if __name__ == "__main__":
    main()
