"""Raw iNaturalist JSON loader.

@file raw_data_loader.py
@brief Loads downloaded raw JSON pages into PostgreSQL tables.
"""

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from inaturalist_client.constants import DATA_DIR, RAW_DOWNLOADS_DIR_NAME
from inaturalist_client.project_config import ProjectConfig
from psycopg import Connection
from psycopg.types.json import Jsonb
from utils import LOGGER

from .constants import UPSERT_OBSERVATION_PHOTO_QUERY_PATH, UPSERT_OBSERVATION_QUERY_PATH, UPSERT_OBSERVER_QUERY_PATH, UPSERT_PROJECT_QUERY_PATH
from .query_loader import load_sql_query
from .taxon_repository import TaxonRepository


class RawDataLoader:
    """Loads downloaded raw iNaturalist pages into PostgreSQL.

    @param database_connection Open PostgreSQL connection.
    @param project_configs Projects expected in the raw data folder.
    @param data_dir Folder containing downloaded project data.
    @param load_date Only load raw data for this snapshot date.
    """

    def __init__(
        self,
        database_connection: Connection,
        project_configs: tuple[ProjectConfig, ...],
        data_dir: Path = DATA_DIR,
        load_date: str | None = None,
    ):
        """Create a raw data loader.

        @param database_connection Open PostgreSQL connection.
        @param project_configs Projects expected in the raw data folder.
        @param data_dir Folder containing downloaded project data.
        @param load_date Only load raw data for this snapshot date.
        """
        self._database_connection = database_connection
        self._project_configs = project_configs
        self._data_dir = data_dir
        self._load_date = load_date
        self._taxon_repository = TaxonRepository(database_connection)

    def load(self) -> dict[str, int]:
        """Load all available raw JSON files into PostgreSQL.

        @return Processed row counts by table.
        """
        load_counts = self._empty_load_counts()
        for project_config in self._project_configs:
            with self._database_connection.transaction():
                self._upsert_project(project_config, load_counts)
            for raw_page_path in self._get_raw_page_paths(project_config.alias):
                self._load_raw_page(raw_page_path, project_config.alias, load_counts)

        self._log_load_counts(load_counts)
        return load_counts

    def _empty_load_counts(self) -> dict[str, int]:
        """Create the load count accumulator.

        @return Empty load counts.
        """
        return {
            "projects": 0,
            "observations": 0,
            "taxa": 0,
            "observers": 0,
            "observation_photos": 0,
        }

    def _get_raw_page_paths(self, project_alias: str) -> list[Path]:
        """Get raw page files for a project.

        @param project_alias Local project alias.
        @return Raw page file paths.
        """
        project_data_dir = self._data_dir / RAW_DOWNLOADS_DIR_NAME / project_alias
        if self._load_date is not None:
            project_date_dir = project_data_dir / self._load_date
            return sorted(project_date_dir.glob(f"{project_alias}_{self._load_date}_page_*.json"))

        return sorted(project_data_dir.glob(f"*/{project_alias}_*_page_*.json"))

    def _load_raw_page(self, raw_page_path: Path, project_alias: str, load_counts: dict[str, int]):
        """Load one raw page JSON file.

        @param raw_page_path Raw page JSON file path.
        @param project_alias Local project alias.
        @param load_counts Processed row counts by table.
        """
        LOGGER.info("Loading raw page into database: %s", raw_page_path)
        download_date = self._parse_raw_page_path(raw_page_path, project_alias)
        with open(raw_page_path) as input_file:
            page_json = json.load(input_file)

        observation_results = page_json.get("results", [])
        loaded_from = str(raw_page_path)
        with self._database_connection.transaction():
            for observation_json in observation_results:
                self._load_observation(
                    project_alias,
                    download_date,
                    loaded_from,
                    observation_json,
                    load_counts,
                )

    def _parse_raw_page_path(self, raw_page_path: Path, project_alias: str) -> date:
        """Parse the snapshot date from a raw page path.

        @param raw_page_path Raw page JSON file path.
        @param project_alias Local project alias.
        @return Download date.
        """
        download_date_text = raw_page_path.parent.name
        file_pattern = rf"^{re.escape(project_alias)}_{download_date_text}_page_(\d+)\.json$"
        file_match = re.match(file_pattern, raw_page_path.name)
        if file_match is None:
            raise ValueError(f"Unexpected raw page file name: {raw_page_path}")

        download_date = datetime.strptime(download_date_text, "%Y%m%d").date()
        return download_date

    def _upsert_project(self, project_config: ProjectConfig, load_counts: dict[str, int]):
        """Upsert one configured project.

        @param project_config Project configuration.
        @param load_counts Processed row counts by table.
        """
        self._database_connection.execute(
            load_sql_query(UPSERT_PROJECT_QUERY_PATH),
            (project_config.alias, project_config.slug, project_config.slug),
        )
        load_counts["projects"] += 1

    def _load_observation(
        self,
        project_alias: str,
        download_date: date,
        loaded_from: str,
        observation_json: dict[str, Any],
        load_counts: dict[str, int],
    ):
        """Load one observation and its nested data.

        @param project_alias Local project alias.
        @param download_date Snapshot date.
        @param loaded_from Source file that supplied the observation.
        @param observation_json Observation JSON object.
        @param load_counts Processed row counts by table.
        """
        observation_id = observation_json.get("id")
        if observation_id is None:
            return

        taxon_json = observation_json.get("taxon") or {}
        observer_json = observation_json.get("user") or {}
        taxon_id = taxon_json.get("id")
        observer_id = observer_json.get("id")

        if taxon_id is not None:
            self._taxon_repository.upsert_taxa([taxon_json], loaded_from)
            load_counts["taxa"] += 1
        if observer_id is not None:
            self._upsert_observer(observer_json, loaded_from, load_counts)

        self._upsert_observation(
            project_alias=project_alias,
            download_date=download_date,
            loaded_from=loaded_from,
            observation_json=observation_json,
            taxon_id=taxon_id,
            observer_id=observer_id,
            load_counts=load_counts,
        )
        self._load_observation_photos(
            project_alias,
            download_date,
            loaded_from,
            observation_id,
            observation_json,
            load_counts,
        )

    def _upsert_observer(
        self,
        observer_json: dict[str, Any],
        loaded_from: str,
        load_counts: dict[str, int],
    ):
        """Upsert observer data.

        @param observer_json Observer JSON object.
        @param loaded_from Source file that supplied the observer.
        @param load_counts Processed row counts by table.
        """
        self._database_connection.execute(
            load_sql_query(UPSERT_OBSERVER_QUERY_PATH),
            (
                observer_json["id"],
                observer_json.get("login"),
                observer_json.get("name"),
                observer_json.get("observations_count"),
                observer_json.get("species_count"),
                loaded_from,
            ),
        )
        load_counts["observers"] += 1

    def _upsert_observation(
        self,
        project_alias: str,
        download_date: date,
        loaded_from: str,
        observation_json: dict[str, Any],
        taxon_id: int | None,
        observer_id: int | None,
        load_counts: dict[str, int],
    ):
        """Upsert an observation row.

        @param project_alias Local project alias.
        @param download_date Snapshot date.
        @param loaded_from Source file that supplied the observation.
        @param observation_json Observation JSON object.
        @param taxon_id iNaturalist taxon ID.
        @param observer_id iNaturalist observer ID.
        @param load_counts Processed row counts by table.
        """
        latitude, longitude = self._get_latitude_longitude(observation_json)
        observed_on, observed_at = self._get_observed_date_time(observation_json)
        self._database_connection.execute(
            load_sql_query(UPSERT_OBSERVATION_QUERY_PATH),
            (
                project_alias,
                download_date,
                observation_json["id"],
                observation_json.get("quality_grade"),
                observation_json.get("species_guess"),
                observed_on,
                observed_at,
                observation_json.get("created_at"),
                observation_json.get("updated_at"),
                longitude,
                latitude,
                observation_json.get("location"),
                observation_json.get("place_guess"),
                observation_json.get("positional_accuracy"),
                observation_json.get("public_positional_accuracy"),
                observation_json.get("geoprivacy"),
                observation_json.get("taxon_geoprivacy"),
                observation_json.get("obscured"),
                observation_json.get("mappable"),
                observation_json.get("captive"),
                Jsonb(observation_json.get("project_ids")),
                Jsonb(observation_json.get("project_ids_with_curator_id")),
                Jsonb(observation_json.get("project_ids_without_curator_id")),
                observation_json.get("identifications_count"),
                observation_json.get("num_identification_agreements"),
                observation_json.get("num_identification_disagreements"),
                taxon_id,
                observer_id,
                loaded_from,
            ),
        )
        load_counts["observations"] += 1

    @staticmethod
    def _get_observed_date_time(observation_json: dict[str, Any]) -> tuple[date | None, datetime | None]:
        """Parse iNaturalist's observation date and optional time fields.

        iNaturalist supplies the calendar date in observed_on and the optional timestamp,
        including its UTC offset, in time_observed_at. No timestamp is inferred when
        time_observed_at is absent.

        @param observation_json iNaturalist observation payload.
        @return Observation calendar date and optional timestamp.
        """
        observed_on_value = observation_json.get("observed_on")
        if observed_on_value is None:
            return None, None

        observed_date = date.fromisoformat(str(observed_on_value)[:10])
        return observed_date, RawDataLoader._parse_observed_timestamp(observation_json.get("time_observed_at"))

    @staticmethod
    def _parse_observed_timestamp(value: Any) -> datetime | None:
        """Parse one optional iNaturalist timestamp.

        @param value Timestamp value returned by iNaturalist.
        @return Parsed timestamp, or None when no time was recorded.
        """
        return datetime.fromisoformat(str(value)) if value is not None else None

    def _load_observation_photos(
        self,
        project_alias: str,
        download_date: date,
        loaded_from: str,
        observation_id: int,
        observation_json: dict[str, Any],
        load_counts: dict[str, int],
    ):
        """Load photos for an observation.

        @param project_alias Local project alias.
        @param download_date Snapshot date.
        @param loaded_from Source file that supplied the photo.
        @param observation_id iNaturalist observation ID.
        @param observation_json Observation JSON object.
        @param load_counts Processed row counts by table.
        """
        for photo_json in observation_json.get("photos") or []:
            photo_id = photo_json.get("id")
            if photo_id is None:
                continue

            original_dimensions = photo_json.get("original_dimensions") or {}
            self._database_connection.execute(
                load_sql_query(UPSERT_OBSERVATION_PHOTO_QUERY_PATH),
                (
                    project_alias,
                    download_date,
                    observation_id,
                    photo_id,
                    photo_json.get("url"),
                    photo_json.get("license_code"),
                    photo_json.get("attribution"),
                    photo_json.get("hidden"),
                    original_dimensions.get("width"),
                    original_dimensions.get("height"),
                    loaded_from,
                ),
            )
            load_counts["observation_photos"] += 1

    def _get_latitude_longitude(self, observation_json: dict[str, Any]) -> tuple[float | None, float | None]:
        """Extract latitude and longitude from GeoJSON coordinates.

        @param observation_json Observation JSON object.
        @return Latitude and longitude.
        """
        geojson = observation_json.get("geojson") or {}
        coordinates = geojson.get("coordinates") or []
        if len(coordinates) < 2:
            return None, None

        longitude = coordinates[0]
        latitude = coordinates[1]
        return latitude, longitude

    def _log_load_counts(self, load_counts: dict[str, int]):
        """Log database load counts.

        @param load_counts Processed row counts by table.
        """
        for table_name, processed_count in load_counts.items():
            LOGGER.info("Database load processed %s rows for %s", processed_count, table_name)
