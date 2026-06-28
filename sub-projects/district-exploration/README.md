# District Exploration

This isolated exploration assigns PostgreSQL observations to Costa Rica districts without changing the database.

## Data Source

District polygons come from INEC's official [Unidad Geoestadística Distrital 2024](https://admin.inec.cr/mapas-cartografia/unidad-geoestadistica-distrital-2024) dataset.

Generated files remain inside this sub-project and are gitignored:

```text
data/district_boundaries.csv
data/district_boundaries.geojson
outputs/observation_districts.csv
```

The boundary CSV stores polygons as WKT. GeoJSON is retained because GeoPandas needs real polygon geometry for the spatial join.

## Setup

Create an isolated environment and install this exploration's dependencies:

```bash
python3 -m venv sub-projects/district-exploration/.venv
sub-projects/district-exploration/.venv/bin/pip install -r sub-projects/district-exploration/requirements.txt
```

## Usage

Download and prepare the district boundaries:

```bash
PYTHONPATH=src sub-projects/district-exploration/.venv/bin/python sub-projects/district-exploration/prepare_district_boundaries.py
```

Read each unique observation from PostgreSQL and create the district-enriched CSV:

```bash
PYTHONPATH=src sub-projects/district-exploration/.venv/bin/python sub-projects/district-exploration/assign_observation_districts.py
```

The second command performs only a `SELECT`. It does not create, update, or delete database data.

The resulting CSV contains:

```text
observation_id
observed_on
observed_year
observed_month
observed_day
location
longitude
latitude
matched_district_code
matched_district
```

Generate one district observation heat map per year:

```bash
PYTHONPATH=src sub-projects/district-exploration/.venv/bin/python sub-projects/district-exploration/generate_yearly_district_heatmaps.py
```

The generated KML files are stored under:

```text
outputs/yearly_heatmaps/district_observations_<YEAR>.kml
```

District colors use the same observation-count bands in every year. Selecting a
district in Google Earth shows its observation count, observations per square
kilometer, and first observation year in the dataset.

## Accuracy

- Public coordinates can be assigned directly to a district polygon.
- Obscured coordinates are approximate and can be assigned to the wrong district near a boundary.
- Observations without coordinates remain in the output with an empty matched district.
- Coordinates outside the INEC polygons also have an empty matched district.
