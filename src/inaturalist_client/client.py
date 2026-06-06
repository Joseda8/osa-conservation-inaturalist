"""iNaturalist client helpers.

@file client.py
@brief Provides object-oriented access to iNaturalist downloads.
"""

from datetime import date
from pathlib import Path
from time import sleep
from typing import Any

from pyinaturalist.constants import API_V2
from pyinaturalist.converters import convert_all_coordinates, convert_all_timestamps
from pyinaturalist.session import post
from requests.exceptions import RequestException
from requests_cache import NEVER_EXPIRE
from utils import LOGGER

from .constants import DATA_DIR, RAW_DATA_DIR_NAME, TMP_DIR
from .observation_fields import OBSERVATION_ANALYSIS_FIELDS
from .project_config import ProjectConfig
from .project_download_summary import ProjectDownloadSummary
from .storage import JsonFileStorage
from .tracking_client_session import _TrackingClientSession


class InaturalistClient(JsonFileStorage):
    """Client for downloading iNaturalist data.

    @param store_files Whether downloads should be saved as JSON by default.
    """

    def __init__(self, store_files: bool = True):
        """Create an iNaturalist client.

        @param store_files Whether downloads should be saved as JSON by default.
        """
        super().__init__(storage_dir=DATA_DIR, store_files=store_files)
        self._session = self._create_session()

    def _create_session(self) -> _TrackingClientSession:
        """Create a pyinaturalist session with project-local storage.

        @return A configured pyinaturalist ClientSession.
        """
        TMP_DIR.mkdir(exist_ok=True)
        LOGGER.debug("Creating pyinaturalist session with cache directory: %s", TMP_DIR)
        return _TrackingClientSession(
            cache_file=TMP_DIR / "pyinat.db",
            cache_control=False,
            expire_after=NEVER_EXPIRE,
            urls_expire_after={"*": NEVER_EXPIRE},
            ratelimit_path=str(TMP_DIR / "pyinat_rate.db"),
            lock_path=str(TMP_DIR / "pyinat.lock"),
            allowable_methods=("GET", "HEAD", "POST"),
        )

    def download_project_observations(
        self,
        project_config: ProjectConfig,
        download_date: date | str | None = None,
        per_page: int = 25,
        request_cooldown_seconds: float = 1.1,
        failure_cooldown_seconds: float = 60.0,
        store: bool | None = None,
    ) -> ProjectDownloadSummary:
        """Download all observation pages for an iNaturalist project.

        @param project_config Project to download.
        @param download_date Date used for the data version.
        @param per_page Number of observations to request in one page.
        @param request_cooldown_seconds Seconds to wait after each successful request.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @param store Overrides the default JSON storage setting when provided.
        @return Summary of the project download.
        """
        if per_page <= 0:
            raise ValueError("per_page must be greater than 0")

        date_version = self._format_download_date(download_date)
        saved_file_paths: list[Path] = []
        current_page = 1
        downloaded_page_count = 0
        total_results = 0
        page_number_padding = 1
        last_observation_id: int | None = None

        LOGGER.info(
            "Starting project download for %s (%s)",
            project_config.alias,
            project_config.slug,
        )

        while True:
            observation_response = self._download_project_observation_page(
                project_config=project_config,
                id_above=last_observation_id,
                per_page=per_page,
                failure_cooldown_seconds=failure_cooldown_seconds,
            )
            if current_page == 1:
                total_results = int(observation_response.get("total_results", 0))
                page_number_padding = self._get_page_number_padding(
                    total_results=total_results,
                    per_page=per_page,
                )

            observation_results = observation_response.get("results", [])
            if not observation_results:
                break

            LOGGER.info(
                "Downloaded page %s for project %s",
                current_page,
                project_config.alias,
            )
            self._log_cache_status()

            raw_file_path = self._raw_page_file_path(
                project_alias=project_config.alias,
                download_date=date_version,
                page=current_page,
                page_number_padding=page_number_padding,
            )
            saved_file_path = self._save_json_if_enabled(
                raw_file_path,
                observation_response,
                store=store,
            )
            if saved_file_path is None:
                LOGGER.info("Observation page was not stored in a file")
            else:
                saved_file_paths.append(saved_file_path)

            downloaded_page_count += 1
            last_observation_id = self._get_last_observation_id(observation_results)
            if len(observation_results) < per_page:
                break

            self._sleep_after_successful_request(request_cooldown_seconds)
            current_page += 1

        LOGGER.info(
            "Completed project download for %s: %s pages, %s total results",
            project_config.alias,
            downloaded_page_count,
            total_results,
        )
        return ProjectDownloadSummary(
            project_alias=project_config.alias,
            download_date=date_version,
            page_count=downloaded_page_count,
            total_results=total_results,
            saved_file_paths=saved_file_paths,
        )

    def _download_project_observation_page(
        self,
        project_config: ProjectConfig,
        id_above: int | None,
        per_page: int,
        failure_cooldown_seconds: float,
    ) -> dict[str, Any]:
        """Download one observation page for an iNaturalist project.

        @param project_config Project to download.
        @param id_above Only include observations with an ID above this value.
        @param per_page Number of observations to request in one page.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return The observation response dictionary.
        """
        request_parameters: dict[str, Any] = {
            "project_id": project_config.slug,
            "fields": OBSERVATION_ANALYSIS_FIELDS,
            "order": "asc",
            "order_by": "id",
            "per_page": per_page,
        }
        if id_above is not None:
            request_parameters["id_above"] = id_above

        return self._get_observations_with_retry(
            request_parameters=request_parameters,
            failure_cooldown_seconds=failure_cooldown_seconds,
        )

    def _get_observations_with_retry(
        self,
        request_parameters: dict[str, Any],
        failure_cooldown_seconds: float,
    ) -> dict[str, Any]:
        """Fetch observations, retrying failed requests with the same batch size.

        @param request_parameters iNaturalist API request parameters.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return The observation response dictionary.
        """
        while True:
            try:
                return self._get_project_observations_response(request_parameters)
            except RequestException as request_error:
                LOGGER.warning(
                    "Observation request failed with per_page=%s: %s",
                    request_parameters["per_page"],
                    request_error,
                )
                self._sleep_after_failed_request(failure_cooldown_seconds)
                LOGGER.warning(
                    "Retrying observation request with the same per_page=%s",
                    request_parameters["per_page"],
                )

    def _get_project_observations_response(self, request_parameters: dict[str, Any]) -> dict[str, Any]:
        """Fetch project observations with the project-local cached session.

        @param request_parameters iNaturalist API request parameters.
        @return Observation response dictionary.
        """
        request_body = {
            request_key: request_value
            for request_key, request_value in request_parameters.items()
            if request_key != "per_page"
        }
        observation_response = post(
            f"{API_V2}/observations",
            headers={"X-HTTP-Method-Override": "GET"},
            json=request_body,
            per_page=request_parameters["per_page"],
            session=self._session,
        ).json()
        observation_response["results"] = convert_all_coordinates(observation_response["results"])
        observation_response["results"] = convert_all_timestamps(observation_response["results"])
        return observation_response

    def _sleep_after_successful_request(self, request_cooldown_seconds: float):
        """Pause after a successful request to reduce API pressure.

        @param request_cooldown_seconds Seconds to wait.
        """
        if request_cooldown_seconds <= 0:
            return

        LOGGER.debug("Waiting %s seconds before the next request", request_cooldown_seconds)
        sleep(request_cooldown_seconds)

    def _sleep_after_failed_request(self, failure_cooldown_seconds: float):
        """Pause after a failed request before retrying.

        @param failure_cooldown_seconds Seconds to wait.
        """
        if failure_cooldown_seconds <= 0:
            return

        LOGGER.warning("Waiting %s seconds before retrying", failure_cooldown_seconds)
        sleep(failure_cooldown_seconds)

    def _format_download_date(self, download_date: date | str | None) -> str:
        """Format the data version date.

        @param download_date Date value to format.
        @return Date string in YYYYMMDD format.
        """
        if download_date is None:
            return date.today().strftime("%Y%m%d")

        if isinstance(download_date, date):
            return download_date.strftime("%Y%m%d")

        return download_date

    def _get_last_observation_id(self, observation_results: list[dict[str, Any]]) -> int:
        """Get the last observation ID from an API response page.

        @param observation_results Observations returned by the API.
        @return Last observation ID in the response page.
        """
        return int(observation_results[-1]["id"])

    def _get_page_number_padding(self, total_results: int, per_page: int) -> int:
        """Calculate filename padding from the maximum possible raw page count.

        @param total_results Total observations reported by iNaturalist.
        @param per_page Number of observations requested in one page.
        @return Number of digits to use for raw page numbers.
        """
        maximum_page_count = max(1, (total_results + per_page - 1) // per_page)
        return len(str(maximum_page_count))

    def _raw_page_file_path(
        self,
        project_alias: str,
        download_date: str,
        page: int,
        page_number_padding: int,
    ) -> Path:
        """Build the raw page JSON path relative to the data folder.

        @param project_alias Short local project alias.
        @param download_date Date string used for the data version.
        @param page Page number included in the file suffix.
        @param page_number_padding Number of digits to use for raw page numbers.
        @return Relative raw page JSON path.
        """
        file_name = f"{project_alias}_{download_date}_page_{page:0{page_number_padding}d}.json"
        return Path(project_alias) / download_date / RAW_DATA_DIR_NAME / file_name

    def _log_cache_status(self):
        """Log whether the last API response came from cache."""
        if self._session._last_response_from_cache:
            LOGGER.info("Observation page was loaded from cache")
        else:
            LOGGER.info("Observation page was downloaded from the iNaturalist API")
