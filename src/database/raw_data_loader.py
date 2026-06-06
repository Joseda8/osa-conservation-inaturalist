"""Raw iNaturalist JSON loader.

@file raw_data_loader.py
@brief Loads downloaded raw JSON pages into PostgreSQL tables.
"""

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from inaturalist_client.constants import DATA_DIR, RAW_DATA_DIR_NAME
from inaturalist_client.project_config import ProjectConfig
from psycopg import Connection
from psycopg.types.json import Jsonb
from utils import LOGGER


class RawDataLoader:
    """Loads downloaded raw iNaturalist pages into PostgreSQL.

    @param database_connection Open PostgreSQL connection.
    @param project_configs Projects expected in the raw data folder.
    @param data_dir Folder containing downloaded project data.
    """

    def __init__(
        self,
        database_connection: Connection,
        project_configs: tuple[ProjectConfig, ...],
        data_dir: Path = DATA_DIR,
    ):
        """Create a raw data loader.

        @param database_connection Open PostgreSQL connection.
        @param project_configs Projects expected in the raw data folder.
        @param data_dir Folder containing downloaded project data.
        """
        self._database_connection = database_connection
        self._project_configs = project_configs
        self._data_dir = data_dir

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
            "raw_observation_pages": 0,
            "observations": 0,
            "taxa": 0,
            "observers": 0,
            "observation_photos": 0,
            "project_observations": 0,
            "observation_field_values": 0,
        }

    def _get_raw_page_paths(self, project_alias: str) -> list[Path]:
        """Get raw page files for a project.

        @param project_alias Local project alias.
        @return Raw page file paths.
        """
        project_data_dir = self._data_dir / project_alias
        return sorted(project_data_dir.glob(f"*/{RAW_DATA_DIR_NAME}/{project_alias}_*_page_*.json"))

    def _load_raw_page(self, raw_page_path: Path, project_alias: str, load_counts: dict[str, int]):
        """Load one raw page JSON file.

        @param raw_page_path Raw page JSON file path.
        @param project_alias Local project alias.
        @param load_counts Processed row counts by table.
        """
        LOGGER.info("Loading raw page into database: %s", raw_page_path)
        download_date, page_number = self._parse_raw_page_path(raw_page_path, project_alias)
        with open(raw_page_path) as input_file:
            page_json = json.load(input_file)

        observation_results = page_json.get("results", [])
        with self._database_connection.transaction():
            self._upsert_raw_observation_page(
                raw_page_path=raw_page_path,
                project_alias=project_alias,
                download_date=download_date,
                page_number=page_number,
                page_json=page_json,
                observation_results=observation_results,
                load_counts=load_counts,
            )
            for observation_json in observation_results:
                self._load_observation(project_alias, download_date, observation_json, load_counts)

    def _parse_raw_page_path(self, raw_page_path: Path, project_alias: str) -> tuple[date, int]:
        """Parse snapshot date and page number from a raw page path.

        @param raw_page_path Raw page JSON file path.
        @param project_alias Local project alias.
        @return Download date and page number.
        """
        download_date_text = raw_page_path.parent.parent.name
        file_pattern = rf"^{re.escape(project_alias)}_{download_date_text}_page_(\d+)\.json$"
        file_match = re.match(file_pattern, raw_page_path.name)
        if file_match is None:
            raise ValueError(f"Unexpected raw page file name: {raw_page_path}")

        download_date = datetime.strptime(download_date_text, "%Y%m%d").date()
        page_number = int(file_match.group(1))
        return download_date, page_number

    def _upsert_project(self, project_config: ProjectConfig, load_counts: dict[str, int]):
        """Upsert one configured project.

        @param project_config Project configuration.
        @param load_counts Processed row counts by table.
        """
        self._database_connection.execute(
            """
            INSERT INTO projects (alias, slug, display_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (alias) DO UPDATE SET
                slug = EXCLUDED.slug,
                display_name = EXCLUDED.display_name
            """,
            (project_config.alias, project_config.slug, project_config.slug),
        )
        load_counts["projects"] += 1

    def _upsert_raw_observation_page(
        self,
        raw_page_path: Path,
        project_alias: str,
        download_date: date,
        page_number: int,
        page_json: dict[str, Any],
        observation_results: list[dict[str, Any]],
        load_counts: dict[str, int],
    ):
        """Upsert raw page metadata and JSON.

        @param raw_page_path Raw page JSON file path.
        @param project_alias Local project alias.
        @param download_date Snapshot date.
        @param page_number Raw page number.
        @param page_json Raw page JSON content.
        @param observation_results Observations in the page.
        @param load_counts Processed row counts by table.
        """
        first_observation_id = self._get_first_observation_id(observation_results)
        last_observation_id = self._get_last_observation_id(observation_results)
        self._database_connection.execute(
            """
            INSERT INTO raw_observation_pages (
                project_alias,
                download_date,
                page_number,
                file_path,
                api_total_results,
                api_page,
                api_per_page,
                result_count,
                first_observation_id,
                last_observation_id,
                raw_json,
                loaded_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
            ON CONFLICT (project_alias, download_date, page_number) DO UPDATE SET
                file_path = EXCLUDED.file_path,
                api_total_results = EXCLUDED.api_total_results,
                api_page = EXCLUDED.api_page,
                api_per_page = EXCLUDED.api_per_page,
                result_count = EXCLUDED.result_count,
                first_observation_id = EXCLUDED.first_observation_id,
                last_observation_id = EXCLUDED.last_observation_id,
                raw_json = EXCLUDED.raw_json,
                loaded_at = now()
            """,
            (
                project_alias,
                download_date,
                page_number,
                str(raw_page_path),
                page_json.get("total_results"),
                page_json.get("page"),
                page_json.get("per_page"),
                len(observation_results),
                first_observation_id,
                last_observation_id,
                Jsonb(page_json),
            ),
        )
        load_counts["raw_observation_pages"] += 1

    def _load_observation(
        self,
        project_alias: str,
        download_date: date,
        observation_json: dict[str, Any],
        load_counts: dict[str, int],
    ):
        """Load one observation and its nested data.

        @param project_alias Local project alias.
        @param download_date Snapshot date.
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
            self._upsert_taxon(taxon_json, load_counts)
        if observer_id is not None:
            self._upsert_observer(observer_json, load_counts)

        self._upsert_observation(
            project_alias=project_alias,
            download_date=download_date,
            observation_json=observation_json,
            taxon_id=taxon_id,
            observer_id=observer_id,
            load_counts=load_counts,
        )
        self._load_observation_photos(project_alias, download_date, observation_id, observation_json, load_counts)
        self._load_project_observations(project_alias, download_date, observation_id, observation_json, load_counts)
        self._load_observation_field_values(project_alias, download_date, observation_id, observation_json, load_counts)

    def _upsert_taxon(self, taxon_json: dict[str, Any], load_counts: dict[str, int]):
        """Upsert taxon data.

        @param taxon_json Taxon JSON object.
        @param load_counts Processed row counts by table.
        """
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
                raw_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                raw_json = EXCLUDED.raw_json
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
                Jsonb(taxon_json),
            ),
        )
        load_counts["taxa"] += 1

    def _upsert_observer(self, observer_json: dict[str, Any], load_counts: dict[str, int]):
        """Upsert observer data.

        @param observer_json Observer JSON object.
        @param load_counts Processed row counts by table.
        """
        self._database_connection.execute(
            """
            INSERT INTO observers (
                observer_id,
                login,
                name,
                observations_count,
                species_count,
                raw_json
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (observer_id) DO UPDATE SET
                login = EXCLUDED.login,
                name = EXCLUDED.name,
                observations_count = EXCLUDED.observations_count,
                species_count = EXCLUDED.species_count,
                raw_json = EXCLUDED.raw_json
            """,
            (
                observer_json["id"],
                observer_json.get("login"),
                observer_json.get("name"),
                observer_json.get("observations_count"),
                observer_json.get("species_count"),
                Jsonb(observer_json),
            ),
        )
        load_counts["observers"] += 1

    def _upsert_observation(
        self,
        project_alias: str,
        download_date: date,
        observation_json: dict[str, Any],
        taxon_id: int | None,
        observer_id: int | None,
        load_counts: dict[str, int],
    ):
        """Upsert an observation row.

        @param project_alias Local project alias.
        @param download_date Snapshot date.
        @param observation_json Observation JSON object.
        @param taxon_id iNaturalist taxon ID.
        @param observer_id iNaturalist observer ID.
        @param load_counts Processed row counts by table.
        """
        latitude, longitude = self._get_latitude_longitude(observation_json)
        observed_details = observation_json.get("observed_on_details") or {}
        created_details = observation_json.get("created_at_details") or {}
        self._database_connection.execute(
            """
            INSERT INTO observations (
                project_alias,
                download_date,
                observation_id,
                uuid,
                uri,
                quality_grade,
                species_guess,
                observed_on,
                observed_year,
                observed_month,
                observed_day,
                created_at,
                created_year,
                created_month,
                created_day,
                updated_at,
                time_zone_offset,
                longitude,
                latitude,
                location,
                place_guess,
                positional_accuracy,
                public_positional_accuracy,
                geoprivacy,
                taxon_geoprivacy,
                obscured,
                mappable,
                captive,
                project_ids,
                project_ids_with_curator_id,
                project_ids_without_curator_id,
                identifications_count,
                num_identification_agreements,
                num_identification_disagreements,
                comments_count,
                faves_count,
                taxon_id,
                observer_id,
                raw_json,
                loaded_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
            )
            ON CONFLICT (project_alias, download_date, observation_id) DO UPDATE SET
                uuid = EXCLUDED.uuid,
                uri = EXCLUDED.uri,
                quality_grade = EXCLUDED.quality_grade,
                species_guess = EXCLUDED.species_guess,
                observed_on = EXCLUDED.observed_on,
                observed_year = EXCLUDED.observed_year,
                observed_month = EXCLUDED.observed_month,
                observed_day = EXCLUDED.observed_day,
                created_at = EXCLUDED.created_at,
                created_year = EXCLUDED.created_year,
                created_month = EXCLUDED.created_month,
                created_day = EXCLUDED.created_day,
                updated_at = EXCLUDED.updated_at,
                time_zone_offset = EXCLUDED.time_zone_offset,
                longitude = EXCLUDED.longitude,
                latitude = EXCLUDED.latitude,
                location = EXCLUDED.location,
                place_guess = EXCLUDED.place_guess,
                positional_accuracy = EXCLUDED.positional_accuracy,
                public_positional_accuracy = EXCLUDED.public_positional_accuracy,
                geoprivacy = EXCLUDED.geoprivacy,
                taxon_geoprivacy = EXCLUDED.taxon_geoprivacy,
                obscured = EXCLUDED.obscured,
                mappable = EXCLUDED.mappable,
                captive = EXCLUDED.captive,
                project_ids = EXCLUDED.project_ids,
                project_ids_with_curator_id = EXCLUDED.project_ids_with_curator_id,
                project_ids_without_curator_id = EXCLUDED.project_ids_without_curator_id,
                identifications_count = EXCLUDED.identifications_count,
                num_identification_agreements = EXCLUDED.num_identification_agreements,
                num_identification_disagreements = EXCLUDED.num_identification_disagreements,
                comments_count = EXCLUDED.comments_count,
                faves_count = EXCLUDED.faves_count,
                taxon_id = EXCLUDED.taxon_id,
                observer_id = EXCLUDED.observer_id,
                raw_json = EXCLUDED.raw_json,
                loaded_at = now()
            """,
            (
                project_alias,
                download_date,
                observation_json["id"],
                observation_json.get("uuid"),
                observation_json.get("uri"),
                observation_json.get("quality_grade"),
                observation_json.get("species_guess"),
                observation_json.get("observed_on"),
                observed_details.get("year"),
                observed_details.get("month"),
                observed_details.get("day"),
                observation_json.get("created_at"),
                created_details.get("year"),
                created_details.get("month"),
                created_details.get("day"),
                observation_json.get("updated_at"),
                observation_json.get("time_zone_offset"),
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
                observation_json.get("comments_count"),
                observation_json.get("faves_count"),
                taxon_id,
                observer_id,
                Jsonb(observation_json),
            ),
        )
        load_counts["observations"] += 1

    def _load_observation_photos(
        self,
        project_alias: str,
        download_date: date,
        observation_id: int,
        observation_json: dict[str, Any],
        load_counts: dict[str, int],
    ):
        """Load photos for an observation.

        @param project_alias Local project alias.
        @param download_date Snapshot date.
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
                """
                INSERT INTO observation_photos (
                    project_alias,
                    download_date,
                    observation_id,
                    photo_id,
                    url,
                    license_code,
                    attribution,
                    hidden,
                    width,
                    height,
                    raw_json
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (project_alias, download_date, observation_id, photo_id) DO UPDATE SET
                    url = EXCLUDED.url,
                    license_code = EXCLUDED.license_code,
                    attribution = EXCLUDED.attribution,
                    hidden = EXCLUDED.hidden,
                    width = EXCLUDED.width,
                    height = EXCLUDED.height,
                    raw_json = EXCLUDED.raw_json
                """,
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
                    Jsonb(photo_json),
                ),
            )
            load_counts["observation_photos"] += 1

    def _load_project_observations(
        self,
        project_alias: str,
        download_date: date,
        observation_id: int,
        observation_json: dict[str, Any],
        load_counts: dict[str, int],
    ):
        """Load project observation relations for an observation.

        @param project_alias Local project alias.
        @param download_date Snapshot date.
        @param observation_id iNaturalist observation ID.
        @param observation_json Observation JSON object.
        @param load_counts Processed row counts by table.
        """
        for project_observation_json in observation_json.get("project_observations") or []:
            project_observation_id = project_observation_json.get("id")
            if project_observation_id is None:
                continue

            project_json = project_observation_json.get("project") or {}
            self._database_connection.execute(
                """
                INSERT INTO project_observations (
                    project_alias,
                    download_date,
                    project_observation_id,
                    observation_id,
                    uuid,
                    inat_project_id,
                    preferences_json,
                    raw_json
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (project_alias, download_date, project_observation_id) DO UPDATE SET
                    observation_id = EXCLUDED.observation_id,
                    uuid = EXCLUDED.uuid,
                    inat_project_id = EXCLUDED.inat_project_id,
                    preferences_json = EXCLUDED.preferences_json,
                    raw_json = EXCLUDED.raw_json
                """,
                (
                    project_alias,
                    download_date,
                    project_observation_id,
                    observation_id,
                    project_observation_json.get("uuid"),
                    project_json.get("id"),
                    Jsonb(project_observation_json.get("preferences")),
                    Jsonb(project_observation_json),
                ),
            )
            load_counts["project_observations"] += 1

    def _load_observation_field_values(
        self,
        project_alias: str,
        download_date: date,
        observation_id: int,
        observation_json: dict[str, Any],
        load_counts: dict[str, int],
    ):
        """Load non-empty observation field values for an observation.

        @param project_alias Local project alias.
        @param download_date Snapshot date.
        @param observation_id iNaturalist observation ID.
        @param observation_json Observation JSON object.
        @param load_counts Processed row counts by table.
        """
        for ofv_index, field_value_json in enumerate(observation_json.get("ofvs") or []):
            if not field_value_json:
                continue

            field_json = field_value_json.get("field") or field_value_json.get("observation_field") or {}
            field_id = field_json.get("id") if isinstance(field_json, dict) else None
            field_name = field_json.get("name") if isinstance(field_json, dict) else None
            field_value = field_value_json.get("value")
            self._database_connection.execute(
                """
                INSERT INTO observation_field_values (
                    project_alias,
                    download_date,
                    observation_id,
                    ofv_index,
                    field_id,
                    field_name,
                    value,
                    raw_json
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (project_alias, download_date, observation_id, ofv_index) DO UPDATE SET
                    field_id = EXCLUDED.field_id,
                    field_name = EXCLUDED.field_name,
                    value = EXCLUDED.value,
                    raw_json = EXCLUDED.raw_json
                """,
                (
                    project_alias,
                    download_date,
                    observation_id,
                    ofv_index,
                    field_id,
                    field_name,
                    str(field_value) if field_value is not None else None,
                    Jsonb(field_value_json),
                ),
            )
            load_counts["observation_field_values"] += 1

    def _get_first_observation_id(self, observation_results: list[dict[str, Any]]) -> int | None:
        """Get the first observation ID in a page.

        @param observation_results Observations in a raw page.
        @return First observation ID, or None.
        """
        if not observation_results:
            return None
        return observation_results[0].get("id")

    def _get_last_observation_id(self, observation_results: list[dict[str, Any]]) -> int | None:
        """Get the last observation ID in a page.

        @param observation_results Observations in a raw page.
        @return Last observation ID, or None.
        """
        if not observation_results:
            return None
        return observation_results[-1].get("id")

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
