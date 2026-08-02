"""iNaturalist client helpers.

@file client.py
@brief Provides object-oriented access to iNaturalist downloads.
"""

from calendar import monthrange
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
    COUNT_REQUEST_PER_PAGE,
    CACHE_DIR,
    DATA_DIR,
    DEFAULT_FAILURE_COOLDOWN_SECONDS,
    DEFAULT_PROJECT_OBSERVATIONS_PER_PAGE,
    DEFAULT_REQUEST_COOLDOWN_SECONDS,
    DEFAULT_STORE_FILES,
    EMPTY_API_RESULT_COUNT,
    FIRST_BATCH_OFFSET,
    FIRST_CLIENT_ERROR_STATUS_CODE,
    FIRST_OBSERVATION_RESULT_INDEX,
    FIRST_SERVER_ERROR_STATUS_CODE,
    INITIAL_RECONCILIATION_SPLIT_DEPTH,
    LAST_OBSERVATION_RESULT_INDEX,
    MINIMUM_RECONCILIATION_BRANCH_SIZE,
    MINIMUM_COOLDOWN_SECONDS,
    MINIMUM_OBSERVATIONS_PER_PAGE,
    MONTHRANGE_LAST_DAY_INDEX,
    RAW_DATA_DIR_NAME,
    RAW_DOWNLOADS_DIR_NAME,
    RAW_PAGE_NUMBER_FILL_CHARACTER,
    RAW_PAGE_NUMBER_PADDING,
    RECONCILIATION_BRANCH_DIVISOR,
    RECONCILE_OBSERVATION_ID_BATCH_SIZE,
    TOO_MANY_REQUESTS_STATUS_CODE,
    TREND_COUNT_PER_PAGE,
    TREND_TAXON_FIELDS,
)
from .observation_fields import OBSERVATION_ANALYSIS_FIELDS
from .project_config import ProjectConfig
from .project_download_summary import ProjectDownloadSummary
from .storage import JsonFileStorage
from .taxon_fields import TAXON_ENRICHMENT_FIELDS
from .tracking_client_session import _TrackingClientSession
from .trend_record import TrendRecord
from .trend_region_config import TrendRegionConfig


class InaturalistClient(JsonFileStorage):
    """Client for downloading iNaturalist data."""

    def __init__(self):
        """Create an iNaturalist client."""
        super().__init__(storage_dir=DATA_DIR)
        self._session = self._create_session()

    def get_monthly_observation_trends(
        self,
        trend_region_config: TrendRegionConfig,
        period_start: date | None = None,
        period_end: date | None = None,
        failure_cooldown_seconds: float = DEFAULT_FAILURE_COOLDOWN_SECONDS,
    ) -> list[TrendRecord]:
        """Get monthly observation count trends for a region.

        @param trend_region_config Region to query.
        @param period_start Optional first date in the trend period.
        @param period_end Optional last date in the trend period.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return Monthly observation count trend records.
        """
        source_endpoint = "observations/histogram"
        source_params = {
            **trend_region_config.request_params,
            "date_field": "observed",
            "interval": "month",
        }
        if period_start is not None:
            source_params["d1"] = period_start.isoformat()
        if period_end is not None:
            source_params["d2"] = period_end.isoformat()

        LOGGER.info("Downloading observed monthly observation trends for %s from %s to %s", trend_region_config.key, period_start or "the beginning", period_end or "now")
        histogram_response = self._get_api_response_with_retry(
            endpoint=source_endpoint,
            request_parameters=source_params,
            failure_cooldown_seconds=failure_cooldown_seconds,
            force_refresh=True,
        )
        month_counts = histogram_response.get("results", {}).get("month", {})
        trend_records = []
        for period_start_text, metric_value in sorted(month_counts.items()):
            period_start = datetime.strptime(period_start_text, "%Y-%m-%d").date()
            period_end = self._get_month_end_date(period_start)
            trend_records.append(
                TrendRecord(
                    region_config=trend_region_config,
                    metric_name="observation_count",
                    period_type="month",
                    period_start=period_start,
                    period_end=period_end,
                    value=int(metric_value),
                    source_endpoint=source_endpoint,
                    source_params=source_params,
                )
            )
        LOGGER.info("Downloaded %s monthly observation trend rows for %s", len(trend_records), trend_region_config.key)
        return trend_records

    def get_monthly_species_count_trends(
        self,
        trend_region_config: TrendRegionConfig,
        period_start: date,
        period_end: date,
        failure_cooldown_seconds: float = DEFAULT_FAILURE_COOLDOWN_SECONDS,
    ) -> list[TrendRecord]:
        """Get monthly species count trend rows for a region.

        @param trend_region_config Region to query.
        @param period_start First date in the monthly trend period.
        @param period_end Last date in the monthly trend period.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return Monthly species count trend records.
        """
        return self._get_monthly_taxon_count_trends(
            trend_region_config=trend_region_config,
            period_start=period_start,
            period_end=period_end,
            endpoint="observations/species_counts",
            metric_name="species_observation_count",
            dimension_type="species_taxon",
            failure_cooldown_seconds=failure_cooldown_seconds,
        )

    def get_monthly_iconic_taxa_count_trends(
        self,
        trend_region_config: TrendRegionConfig,
        period_start: date,
        period_end: date,
        failure_cooldown_seconds: float = DEFAULT_FAILURE_COOLDOWN_SECONDS,
    ) -> list[TrendRecord]:
        """Get monthly iconic taxon count trend rows for a region.

        @param trend_region_config Region to query.
        @param period_start First date in the monthly trend period.
        @param period_end Last date in the monthly trend period.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return Monthly iconic taxon count trend records.
        """
        return self._get_monthly_taxon_count_trends(
            trend_region_config=trend_region_config,
            period_start=period_start,
            period_end=period_end,
            endpoint="observations/iconic_taxa_species_counts",
            metric_name="iconic_taxon_species_count",
            dimension_type="iconic_taxon",
            failure_cooldown_seconds=failure_cooldown_seconds,
        )

    def _get_monthly_taxon_count_trends(
        self,
        trend_region_config: TrendRegionConfig,
        period_start: date,
        period_end: date,
        endpoint: str,
        metric_name: str,
        dimension_type: str,
        failure_cooldown_seconds: float,
    ) -> list[TrendRecord]:
        """Get monthly taxon count trend rows for a region.

        @param trend_region_config Region to query.
        @param period_start First date in the monthly trend period.
        @param period_end Last date in the monthly trend period.
        @param endpoint iNaturalist aggregate endpoint.
        @param metric_name Metric name to store.
        @param dimension_type Dimension type to store.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return Monthly taxon count trend records.
        """
        source_params = {
            **trend_region_config.request_params,
            "d1": period_start.isoformat(),
            "d2": period_end.isoformat(),
            "fields": TREND_TAXON_FIELDS,
            "per_page": TREND_COUNT_PER_PAGE,
        }
        trend_records: list[TrendRecord] = []
        for response_row in self._get_paginated_trend_count_rows(
            endpoint=endpoint,
            source_params=source_params,
            failure_cooldown_seconds=failure_cooldown_seconds,
        ):
            taxon = response_row.get("taxon", {})
            taxon_id = taxon.get("id")
            if taxon_id is None:
                continue

            taxon_name = taxon.get("name") or str(taxon_id)
            dimension_label = taxon.get("preferred_common_name") or taxon_name
            trend_records.append(
                TrendRecord(
                    region_config=trend_region_config,
                    metric_name=metric_name,
                    period_type="month",
                    period_start=period_start,
                    period_end=period_end,
                    value=int(response_row.get("count", EMPTY_API_RESULT_COUNT)),
                    source_endpoint=endpoint,
                    source_params=source_params,
                    dimension_type=dimension_type,
                    dimension_id=str(taxon_id),
                    dimension_label=dimension_label,
                )
            )

        LOGGER.info("Downloaded %s %s trend rows for %s from %s to %s", len(trend_records), metric_name, trend_region_config.key, period_start, period_end)
        return trend_records

    def _get_paginated_trend_count_rows(
        self,
        endpoint: str,
        source_params: dict[str, Any],
        failure_cooldown_seconds: float,
    ) -> list[dict[str, Any]]:
        """Get all rows from a paginated trends count endpoint.

        @param endpoint iNaturalist aggregate endpoint.
        @param source_params Base API parameters.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return Count response rows.
        """
        response_rows: list[dict[str, Any]] = []
        page_number = 1
        while True:
            request_params = {**source_params, "page": page_number}
            trend_count_response = self._get_api_response_with_retry(
                endpoint=endpoint,
                request_parameters=request_params,
                failure_cooldown_seconds=failure_cooldown_seconds,
                force_refresh=True,
            )
            page_rows = trend_count_response.get("results", [])
            response_rows.extend(page_rows)

            total_results = int(trend_count_response.get("total_results", len(response_rows)))
            if len(response_rows) >= total_results or not page_rows:
                return response_rows

            page_number += 1

    def _get_month_end_date(self, period_start: date) -> date:
        """Get the last date of the month containing a period start date.

        @param period_start First date in a monthly period.
        @return Last date in the same month.
        """
        last_day = monthrange(period_start.year, period_start.month)[MONTHRANGE_LAST_DAY_INDEX]
        return date(period_start.year, period_start.month, last_day)

    def get_taxa(
        self,
        taxon_ids: list[int],
        request_cooldown_seconds: float = DEFAULT_REQUEST_COOLDOWN_SECONDS,
        failure_cooldown_seconds: float = DEFAULT_FAILURE_COOLDOWN_SECONDS,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        """Get taxon metadata for one enrichment batch.

        @param taxon_ids iNaturalist taxon IDs to fetch.
        @param request_cooldown_seconds Seconds to wait after a successful request.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @param force_refresh Whether to bypass cached responses.
        @return Taxon API response rows.
        """
        if not taxon_ids:
            return []

        requested_taxon_ids = sorted(set(taxon_ids))
        endpoint_ids = ",".join(str(taxon_id) for taxon_id in requested_taxon_ids)
        taxon_response = self._get_api_response_with_retry(
            endpoint=f"taxa/{endpoint_ids}",
            request_parameters={"fields": TAXON_ENRICHMENT_FIELDS},
            failure_cooldown_seconds=failure_cooldown_seconds,
            force_refresh=force_refresh,
        )
        taxon_rows = taxon_response.get("results", [])
        returned_taxon_ids = {
            int(taxon_row["id"])
            for taxon_row in taxon_rows
            if taxon_row.get("id") is not None
        }
        missing_taxon_ids = sorted(set(requested_taxon_ids) - returned_taxon_ids)
        if missing_taxon_ids:
            raise RuntimeError(
                "iNaturalist omitted requested taxon IDs: "
                + ", ".join(str(taxon_id) for taxon_id in missing_taxon_ids)
            )

        LOGGER.info("Downloaded %s taxonomy rows", len(taxon_rows))
        self._log_cache_status("Taxonomy batch")
        self._sleep_after_downloaded_request(request_cooldown_seconds)
        return taxon_rows

    def get_stale_observation_ids(
        self,
        project_config: ProjectConfig,
        observation_ids: set[int],
        failure_cooldown_seconds: float = DEFAULT_FAILURE_COOLDOWN_SECONDS,
    ) -> set[int]:
        """Get local observation IDs that no longer belong to a project.

        @param project_config Project to inspect.
        @param observation_ids Local observation IDs to check.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return Observation IDs that are not currently in the project.
        """
        stale_observation_ids: set[int] = set()
        sorted_observation_ids = sorted(observation_ids)

        LOGGER.info("Checking %s local observation IDs for project %s", len(sorted_observation_ids), project_config.alias)
        total_batches = (
            len(sorted_observation_ids) + RECONCILE_OBSERVATION_ID_BATCH_SIZE - 1
        ) // RECONCILE_OBSERVATION_ID_BATCH_SIZE
        for batch_start in range(
            FIRST_BATCH_OFFSET,
            len(sorted_observation_ids),
            RECONCILE_OBSERVATION_ID_BATCH_SIZE,
        ):
            batch_number = (batch_start // RECONCILE_OBSERVATION_ID_BATCH_SIZE) + 1
            observation_id_batch = sorted_observation_ids[
                batch_start : batch_start + RECONCILE_OBSERVATION_ID_BATCH_SIZE
            ]
            LOGGER.info("Request batch %s/%s for project %s with %s local observation IDs", batch_number, total_batches, project_config.alias, len(observation_id_batch))
            stale_observation_ids.update(
                self._get_stale_observation_ids_from_batch(
                    project_config=project_config,
                    observation_ids=observation_id_batch,
                    batch_number=batch_number,
                    failure_cooldown_seconds=failure_cooldown_seconds,
                )
            )

        LOGGER.info("Found %s stale local observation IDs for project %s", len(stale_observation_ids), project_config.alias)
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
        LOGGER.info("Request batch %s for project %s matched %s/%s local observation IDs", batch_number, project_config.alias, current_observation_count, len(observation_ids))
        if current_observation_count == len(observation_ids):
            LOGGER.info("No stale observation IDs found in request batch %s for project %s", batch_number, project_config.alias)
            return set()

        expected_stale_count = len(observation_ids) - current_observation_count
        stale_observation_ids = self._find_stale_observation_ids(
            project_config=project_config,
            observation_ids=observation_ids,
            expected_stale_count=expected_stale_count,
            batch_number=batch_number,
            failure_cooldown_seconds=failure_cooldown_seconds,
        )
        LOGGER.info("Request batch %s for project %s found %s stale observation IDs", batch_number, project_config.alias, len(stale_observation_ids))
        return stale_observation_ids

    def _find_stale_observation_ids(
        self,
        project_config: ProjectConfig,
        observation_ids: list[int],
        expected_stale_count: int,
        batch_number: int,
        failure_cooldown_seconds: float,
    ) -> set[int]:
        """Find stale observation IDs by iteratively splitting a mismatched ID batch.

        @param project_config Project to inspect.
        @param observation_ids Local observation IDs to check.
        @param expected_stale_count Number of stale IDs still expected in this branch.
        @param batch_number Reconciliation request batch number.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @return IDs from the batch that are not currently in the project.
        """
        stale_observation_ids: set[int] = set()
        search_stack = [(observation_ids, expected_stale_count, INITIAL_RECONCILIATION_SPLIT_DEPTH)]

        while search_stack and len(stale_observation_ids) < expected_stale_count:
            branch_observation_ids, branch_stale_count, split_depth = search_stack.pop()
            if branch_stale_count <= EMPTY_API_RESULT_COUNT:
                continue

            if branch_stale_count == len(branch_observation_ids):
                LOGGER.info("Found %s stale observation IDs in request batch %s for project %s", len(branch_observation_ids), batch_number, project_config.alias)
                stale_observation_ids.update(branch_observation_ids)
                continue

            if len(branch_observation_ids) == MINIMUM_RECONCILIATION_BRANCH_SIZE:
                LOGGER.info("Found stale observation ID %s in request batch %s for project %s", branch_observation_ids[FIRST_OBSERVATION_RESULT_INDEX], batch_number, project_config.alias)
                stale_observation_ids.add(branch_observation_ids[FIRST_OBSERVATION_RESULT_INDEX])
                continue

            middle_index = len(branch_observation_ids) // RECONCILIATION_BRANCH_DIVISOR
            left_observation_ids = branch_observation_ids[:middle_index]
            right_observation_ids = branch_observation_ids[middle_index:]
            left_current_observation_count = self._count_observation_ids_in_project(
                project_config=project_config,
                observation_ids=left_observation_ids,
                failure_cooldown_seconds=failure_cooldown_seconds,
            )
            left_stale_count = len(left_observation_ids) - left_current_observation_count
            right_stale_count = branch_stale_count - left_stale_count
            LOGGER.info("Narrowing request batch %s for project %s: %s/%s left-branch IDs matched at split depth %s", batch_number, project_config.alias, left_current_observation_count, len(left_observation_ids), split_depth + 1)

            search_stack.append((right_observation_ids, right_stale_count, split_depth + 1))
            search_stack.append((left_observation_ids, left_stale_count, split_depth + 1))

        if len(stale_observation_ids) >= expected_stale_count:
            LOGGER.info("Found all %s expected stale IDs for request batch %s", expected_stale_count, batch_number)
        return stale_observation_ids

    def _create_session(self) -> _TrackingClientSession:
        """Create a pyinaturalist session with project-local storage.

        @return A configured pyinaturalist ClientSession.
        """
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        LOGGER.debug("Creating pyinaturalist session with cache directory: %s", CACHE_DIR)
        return _TrackingClientSession(
            cache_file=CACHE_DIR / "pyinat.db",
            cache_control=False,
            expire_after=NEVER_EXPIRE,
            urls_expire_after={"*": NEVER_EXPIRE},
            ratelimit_path=str(CACHE_DIR / "pyinat_rate.db"),
            lock_path=str(CACHE_DIR / "pyinat.lock"),
            allowable_methods=("GET", "HEAD", "POST"),
        )

    def download_project_observations(
        self,
        project_config: ProjectConfig,
        download_date: date | str | None = None,
        per_page: int = DEFAULT_PROJECT_OBSERVATIONS_PER_PAGE,
        request_cooldown_seconds: float = DEFAULT_REQUEST_COOLDOWN_SECONDS,
        failure_cooldown_seconds: float = DEFAULT_FAILURE_COOLDOWN_SECONDS,
        updated_since: datetime | str | None = None,
        force_refresh: bool = False,
        store: bool = DEFAULT_STORE_FILES,
    ) -> ProjectDownloadSummary:
        """Download all observation pages for an iNaturalist project.

        @param project_config Project to download.
        @param download_date Date used for the data version.
        @param per_page Number of observations to request in one page.
        @param request_cooldown_seconds Seconds to wait after each successful request.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @param updated_since Only include observations updated since this time.
        @param force_refresh Whether to bypass cached responses.
        @param store Whether to save downloaded pages as JSON files.
        @return Summary of the project download.
        """
        date_version = self._format_download_date(download_date)
        saved_file_paths: list[Path] = []
        current_page = 1
        downloaded_page_count = EMPTY_API_RESULT_COUNT
        total_results = EMPTY_API_RESULT_COUNT
        # The final observation ID from each page is the cursor for the next API request.
        last_observation_id: int | None = None

        LOGGER.info("Starting project download for %s (%s)", project_config.alias, project_config.slug)
        if updated_since is not None:
            LOGGER.info("Downloading observations updated since %s", updated_since)

        while True:
            observation_response = self._download_project_observation_page(project_config=project_config, id_above=last_observation_id, per_page=per_page, failure_cooldown_seconds=failure_cooldown_seconds, updated_since=updated_since, force_refresh=force_refresh)
            # The API reports the project total with the first page response.
            if current_page == 1:
                total_results = int(observation_response.get("total_results", EMPTY_API_RESULT_COUNT))

            observation_results = observation_response.get("results", [])
            # An empty page means the cursor has passed the final matching observation.
            if not observation_results:
                break

            LOGGER.info("Downloaded page %s for project %s", current_page, project_config.alias)
            self._log_cache_status()

            raw_file_path = self._raw_page_file_path(project_alias=project_config.alias, download_date=date_version, page=current_page)
            saved_file_path = self._save_json_if_enabled(raw_file_path, observation_response, store=store)
            if saved_file_path is not None:
                saved_file_paths.append(saved_file_path)

            downloaded_page_count += 1
            # Request only IDs above this page's final ID to advance without duplicates
            last_observation_id = self._get_last_observation_id(observation_results)
            # A short page is the final API page because it returned fewer rows than requested
            if len(observation_results) < per_page:
                break

            self._sleep_after_downloaded_request(request_cooldown_seconds)
            current_page += 1

        LOGGER.info("Completed project download for %s: %s pages, %s total results", project_config.alias, downloaded_page_count, total_results)
        return ProjectDownloadSummary(project_alias=project_config.alias, download_date=date_version, page_count=downloaded_page_count, total_results=total_results, saved_file_paths=saved_file_paths)

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

        return self._get_observations_with_retry(request_parameters=request_parameters, failure_cooldown_seconds=failure_cooldown_seconds, force_refresh=force_refresh)

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
            "per_page": COUNT_REQUEST_PER_PAGE,
        }

        observation_response = self._get_observations_with_retry(request_parameters=request_parameters, failure_cooldown_seconds=failure_cooldown_seconds, force_refresh=True)
        return int(observation_response.get("total_results", EMPTY_API_RESULT_COUNT))

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
                LOGGER.warning("Observation request failed with per_page=%s: %s", request_parameters["per_page"], request_error)
                self._sleep_after_failed_request(failure_cooldown_seconds)
                LOGGER.warning("Retrying observation request with the same per_page=%s", request_parameters["per_page"])

    def _get_api_response_with_retry(
        self,
        endpoint: str,
        request_parameters: dict[str, Any],
        failure_cooldown_seconds: float,
        force_refresh: bool,
    ) -> dict[str, Any]:
        """Fetch an iNaturalist API response, retrying failed requests.

        @param endpoint API endpoint path relative to API_V2.
        @param request_parameters iNaturalist API request parameters.
        @param failure_cooldown_seconds Seconds to wait after failed requests.
        @param force_refresh Whether to bypass cached responses.
        @return API response dictionary.
        """
        while True:
            try:
                return post(
                    f"{API_V2}/{endpoint}",
                    headers={"X-HTTP-Method-Override": "GET"},
                    json=request_parameters,
                    session=self._session,
                    force_refresh=force_refresh,
                ).json()
            except RequestException as request_error:
                response = request_error.response
                if (
                    response is not None
                    and FIRST_CLIENT_ERROR_STATUS_CODE <= response.status_code < FIRST_SERVER_ERROR_STATUS_CODE
                    and response.status_code != TOO_MANY_REQUESTS_STATUS_CODE
                ):
                    LOGGER.error("API request was rejected for %s: %s", endpoint, response.text)
                    raise

                LOGGER.warning("API request failed for %s: %s", endpoint, request_error)
                self._sleep_after_failed_request(failure_cooldown_seconds)
                LOGGER.warning("Retrying API request for %s", endpoint)

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

        if request_cooldown_seconds <= MINIMUM_COOLDOWN_SECONDS:
            return

        LOGGER.debug("Waiting %s seconds before the next request", request_cooldown_seconds)
        sleep(request_cooldown_seconds)

    def _sleep_after_failed_request(self, failure_cooldown_seconds: float):
        """Pause after a failed request before retrying.

        @param failure_cooldown_seconds Seconds to wait.
        """
        if failure_cooldown_seconds <= MINIMUM_COOLDOWN_SECONDS:
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
        return int(observation_results[LAST_OBSERVATION_RESULT_INDEX]["id"])

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
        file_name = f"{project_alias}_{download_date}_page_{page:{RAW_PAGE_NUMBER_FILL_CHARACTER}{RAW_PAGE_NUMBER_PADDING}d}.json"
        return Path(RAW_DOWNLOADS_DIR_NAME) / project_alias / download_date / RAW_DATA_DIR_NAME / file_name

    def _log_cache_status(self, resource_name: str = "Observation page"):
        """Log whether the last API response came from cache.

        @param resource_name Name of the downloaded resource.
        """
        if self._session._last_response_from_cache:
            LOGGER.info("%s was loaded from cache", resource_name)
        else:
            LOGGER.info("%s was downloaded from the iNaturalist API", resource_name)
