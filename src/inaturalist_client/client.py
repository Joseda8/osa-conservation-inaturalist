"""iNaturalist client helpers.

@file client.py
@brief Provides object-oriented access to iNaturalist downloads.
"""

from datetime import date, datetime
from pathlib import Path
from time import sleep
from typing import Any

from pyinaturalist.constants import API_V2
from pyinaturalist.converters import convert_all_coordinates, convert_all_timestamps
from pyinaturalist.session import post
from requests.exceptions import RequestException
from requests_cache import NEVER_EXPIRE
from utils import LOGGER

from .constants import (
    DATA_DIR,
    RAW_DATA_DIR_NAME,
    RAW_PAGE_NUMBER_PADDING,
    RECONCILE_OBSERVATION_ID_BATCH_SIZE,
    TMP_DIR,
)
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

    def get_stale_observation_ids(
        self,
        project_config: ProjectConfig,
        observation_ids: set[int],
        failure_cooldown_seconds: float = 60.0,
    ) -> set[int]:
        """Get local observation IDs that no longer belong to a project.

        @param project_config Project to inspect.
        @param observation_ids Local observation IDs to check.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return Observation IDs that are not currently in the project.
        """
        stale_observation_ids: set[int] = set()
        sorted_observation_ids = sorted(observation_ids)

        LOGGER.info(
            "Checking %s local observation IDs for project %s",
            len(sorted_observation_ids),
            project_config.alias,
        )
        total_batches = (
            len(sorted_observation_ids) + RECONCILE_OBSERVATION_ID_BATCH_SIZE - 1
        ) // RECONCILE_OBSERVATION_ID_BATCH_SIZE
        for batch_start in range(
            0,
            len(sorted_observation_ids),
            RECONCILE_OBSERVATION_ID_BATCH_SIZE,
        ):
            batch_number = (batch_start // RECONCILE_OBSERVATION_ID_BATCH_SIZE) + 1
            observation_id_batch = sorted_observation_ids[
                batch_start : batch_start + RECONCILE_OBSERVATION_ID_BATCH_SIZE
            ]
            LOGGER.info(
                "Request batch %s/%s for project %s with %s local observation IDs",
                batch_number,
                total_batches,
                project_config.alias,
                len(observation_id_batch),
            )
            stale_observation_ids.update(
                self._get_stale_observation_ids_from_batch(
                    project_config=project_config,
                    observation_ids=observation_id_batch,
                    batch_number=batch_number,
                    failure_cooldown_seconds=failure_cooldown_seconds,
                )
            )

        LOGGER.info(
            "Found %s stale local observation IDs for project %s",
            len(stale_observation_ids),
            project_config.alias,
        )
        return stale_observation_ids

    def _get_stale_observation_ids_from_batch(
        self,
        project_config: ProjectConfig,
        observation_ids: list[int],
        batch_number: int,
        failure_cooldown_seconds: float,
    ) -> set[int]:
        """Get stale IDs from one local observation ID batch.

        @param project_config Project to inspect.
        @param observation_ids Local observation IDs to check.
        @param batch_number Reconciliation request batch number.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return IDs from the batch that are not currently in the project.
        """
        current_observation_count = self._count_observation_ids_in_project(
            project_config=project_config,
            observation_ids=observation_ids,
            failure_cooldown_seconds=failure_cooldown_seconds,
        )
        LOGGER.info(
            "Request batch %s for project %s matched %s/%s local observation IDs",
            batch_number,
            project_config.alias,
            current_observation_count,
            len(observation_ids),
        )
        if current_observation_count == len(observation_ids):
            LOGGER.info(
                "No stale observation IDs found in request batch %s for project %s",
                batch_number,
                project_config.alias,
            )
            return set()

        expected_stale_count = len(observation_ids) - current_observation_count
        stale_observation_ids = self._find_stale_observation_ids(
            project_config=project_config,
            observation_ids=observation_ids,
            expected_stale_count=expected_stale_count,
            batch_number=batch_number,
            split_depth=0,
            failure_cooldown_seconds=failure_cooldown_seconds,
        )
        LOGGER.info(
            "Request batch %s for project %s found %s stale observation IDs",
            batch_number,
            project_config.alias,
            len(stale_observation_ids),
        )
        return stale_observation_ids

    def _find_stale_observation_ids(
        self,
        project_config: ProjectConfig,
        observation_ids: list[int],
        expected_stale_count: int,
        batch_number: int,
        split_depth: int,
        failure_cooldown_seconds: float,
    ) -> set[int]:
        """Find stale observation IDs by splitting a mismatched ID batch.

        @param project_config Project to inspect.
        @param observation_ids Local observation IDs to check.
        @param expected_stale_count Number of stale IDs still expected in this branch.
        @param batch_number Reconciliation request batch number.
        @param split_depth Current binary search depth.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return IDs from the batch that are not currently in the project.
        """
        if expected_stale_count <= 0:
            return set()

        if expected_stale_count == len(observation_ids):
            LOGGER.info(
                "Found %s stale observation IDs in request batch %s for project %s",
                len(observation_ids),
                batch_number,
                project_config.alias,
            )
            return set(observation_ids)

        current_observation_count = self._count_observation_ids_in_project(
            project_config=project_config,
            observation_ids=observation_ids,
            failure_cooldown_seconds=failure_cooldown_seconds,
        )
        LOGGER.info(
            "Narrowing request batch %s for project %s: %s/%s IDs matched at split depth %s",
            batch_number,
            project_config.alias,
            current_observation_count,
            len(observation_ids),
            split_depth,
        )
        actual_stale_count = len(observation_ids) - current_observation_count
        if current_observation_count == len(observation_ids):
            return set()

        if current_observation_count == 0:
            LOGGER.info(
                "Found %s stale observation IDs in request batch %s for project %s",
                len(observation_ids),
                batch_number,
                project_config.alias,
            )
            return set(observation_ids)

        if len(observation_ids) == 1:
            LOGGER.info(
                "Found stale observation ID %s in request batch %s for project %s",
                observation_ids[0],
                batch_number,
                project_config.alias,
            )
            return {observation_ids[0]}

        middle_index = len(observation_ids) // 2
        left_observation_ids = observation_ids[:middle_index]
        right_observation_ids = observation_ids[middle_index:]
        left_current_observation_count = self._count_observation_ids_in_project(
            project_config=project_config,
            observation_ids=left_observation_ids,
            failure_cooldown_seconds=failure_cooldown_seconds,
        )
        left_stale_count = len(left_observation_ids) - left_current_observation_count
        LOGGER.info(
            "Narrowing request batch %s for project %s: %s/%s left-branch IDs matched at split depth %s",
            batch_number,
            project_config.alias,
            left_current_observation_count,
            len(left_observation_ids),
            split_depth + 1,
        )

        stale_observation_ids = self._find_stale_observation_ids(
            project_config=project_config,
            observation_ids=left_observation_ids,
            expected_stale_count=left_stale_count,
            batch_number=batch_number,
            split_depth=split_depth + 1,
            failure_cooldown_seconds=failure_cooldown_seconds,
        )
        if len(stale_observation_ids) >= actual_stale_count:
            LOGGER.info(
                "Found all %s expected stale IDs for request batch %s at split depth %s",
                actual_stale_count,
                batch_number,
                split_depth,
            )
            return stale_observation_ids

        right_stale_count = actual_stale_count - len(stale_observation_ids)
        return stale_observation_ids | self._find_stale_observation_ids(
            project_config=project_config,
            observation_ids=right_observation_ids,
            expected_stale_count=right_stale_count,
            batch_number=batch_number,
            split_depth=split_depth + 1,
            failure_cooldown_seconds=failure_cooldown_seconds,
        )

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
        updated_since: datetime | str | None = None,
        force_refresh: bool = False,
        store: bool | None = None,
    ) -> ProjectDownloadSummary:
        """Download all observation pages for an iNaturalist project.

        @param project_config Project to download.
        @param download_date Date used for the data version.
        @param per_page Number of observations to request in one page.
        @param request_cooldown_seconds Seconds to wait after each successful request.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @param updated_since Only include observations updated since this time.
        @param force_refresh Whether to bypass cached responses.
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
        last_observation_id: int | None = None

        LOGGER.info(
            "Starting project download for %s (%s)",
            project_config.alias,
            project_config.slug,
        )
        if updated_since is not None:
            LOGGER.info("Downloading observations updated since %s", updated_since)

        while True:
            observation_response = self._download_project_observation_page(
                project_config=project_config,
                id_above=last_observation_id,
                per_page=per_page,
                failure_cooldown_seconds=failure_cooldown_seconds,
                updated_since=updated_since,
                force_refresh=force_refresh,
            )
            if current_page == 1:
                total_results = int(observation_response.get("total_results", 0))

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

            self._sleep_after_downloaded_request(request_cooldown_seconds)
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
        updated_since: datetime | str | None,
        force_refresh: bool,
    ) -> dict[str, Any]:
        """Download one observation page for an iNaturalist project.

        @param project_config Project to download.
        @param id_above Only include observations with an ID above this value.
        @param per_page Number of observations to request in one page.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @param updated_since Only include observations updated since this time.
        @param force_refresh Whether to bypass cached responses.
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
        if updated_since is not None:
            request_parameters["updated_since"] = self._format_api_datetime(updated_since)

        return self._get_observations_with_retry(
            request_parameters=request_parameters,
            failure_cooldown_seconds=failure_cooldown_seconds,
            force_refresh=force_refresh,
        )

    def _count_observation_ids_in_project(
        self,
        project_config: ProjectConfig,
        observation_ids: list[int],
        failure_cooldown_seconds: float,
    ) -> int:
        """Count how many local observation IDs are still in a project.

        @param project_config Project to inspect.
        @param observation_ids Local observation IDs to check.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return Number of given observation IDs still in the project.
        """
        request_parameters: dict[str, Any] = {
            "id": observation_ids,
            "project_id": project_config.slug,
            "fields": {
                "id": True,
            },
            "order": "asc",
            "order_by": "id",
            "per_page": 1,
        }

        observation_response = self._get_observations_with_retry(
            request_parameters=request_parameters,
            failure_cooldown_seconds=failure_cooldown_seconds,
            force_refresh=True,
        )
        return int(observation_response.get("total_results", 0))

    def _get_observations_with_retry(
        self,
        request_parameters: dict[str, Any],
        failure_cooldown_seconds: float,
        force_refresh: bool,
    ) -> dict[str, Any]:
        """Fetch observations, retrying failed requests with the same batch size.

        @param request_parameters iNaturalist API request parameters.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @param force_refresh Whether to bypass cached responses.
        @return The observation response dictionary.
        """
        while True:
            try:
                return self._get_project_observations_response(request_parameters, force_refresh)
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

    def _get_project_observations_response(
        self,
        request_parameters: dict[str, Any],
        force_refresh: bool,
    ) -> dict[str, Any]:
        """Fetch project observations with the project-local cached session.

        @param request_parameters iNaturalist API request parameters.
        @param force_refresh Whether to bypass cached responses.
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
            force_refresh=force_refresh,
        ).json()
        observation_response["results"] = convert_all_coordinates(observation_response["results"])
        observation_response["results"] = convert_all_timestamps(observation_response["results"])
        return observation_response

    def _sleep_after_downloaded_request(self, request_cooldown_seconds: float):
        """Pause after a successful API request to reduce API pressure.

        @param request_cooldown_seconds Seconds to wait.
        """
        if self._session._last_response_from_cache:
            return

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

    def _format_api_datetime(self, api_datetime: datetime | str) -> str:
        """Format a datetime value for iNaturalist API filters.

        @param api_datetime Datetime value or preformatted datetime string.
        @return ISO formatted datetime string.
        """
        if isinstance(api_datetime, str):
            return api_datetime

        return api_datetime.isoformat()

    def _get_last_observation_id(self, observation_results: list[dict[str, Any]]) -> int:
        """Get the last observation ID from an API response page.

        @param observation_results Observations returned by the API.
        @return Last observation ID in the response page.
        """
        return int(observation_results[-1]["id"])

    def _raw_page_file_path(
        self,
        project_alias: str,
        download_date: str,
        page: int,
    ) -> Path:
        """Build the raw page JSON path relative to the data folder.

        @param project_alias Short local project alias.
        @param download_date Date string used for the data version.
        @param page Page number included in the file suffix.
        @return Relative raw page JSON path.
        """
        file_name = f"{project_alias}_{download_date}_page_{page:0{RAW_PAGE_NUMBER_PADDING}d}.json"
        return Path(project_alias) / download_date / RAW_DATA_DIR_NAME / file_name

    def _log_cache_status(self):
        """Log whether the last API response came from cache."""
        if self._session._last_response_from_cache:
            LOGGER.info("Observation page was loaded from cache")
        else:
            LOGGER.info("Observation page was downloaded from the iNaturalist API")
