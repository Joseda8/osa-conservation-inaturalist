"""iNaturalist client helpers.

@file client.py
@brief Provides object-oriented access to iNaturalist downloads.
"""

from typing import Any

from pyinaturalist.v2.observations import get_observations
from pyinaturalist.session import ClientSession
from utils import LOGGER

from .constants import DATA_DIR, OSA_USER_LOGIN, TMP_DIR
from .storage import JsonFileStorage


class _TrackingClientSession(ClientSession):
    """ClientSession that tracks whether the last response came from cache."""

    def __init__(self, **kwargs):
        """Create a tracking ClientSession.

        @param kwargs ClientSession configuration values.
        """
        super().__init__(**kwargs)
        self._last_response_from_cache = False

    def send(self, *args, **kwargs):
        """Send a request and remember whether the response came from cache.

        @param args Positional arguments forwarded to ClientSession.send.
        @param kwargs Keyword arguments forwarded to ClientSession.send.
        @return API response.
        """
        response = super().send(*args, **kwargs)
        self._last_response_from_cache = bool(getattr(response, "from_cache", False))
        return response


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
            ratelimit_path=str(TMP_DIR / "pyinat_rate.db"),
            lock_path=str(TMP_DIR / "pyinat.lock"),
        )

    def get_osa_observations(
        self,
        output_file_name: str | None = None,
        per_page: int = 200,
        store: bool | None = None,
    ) -> dict[str, Any]:
        """Fetch observations from the OSA Conservation iNaturalist account.

        @param output_file_name File name to use when storing the response.
        @param per_page Number of observations to request in one page.
        @param store Overrides the default JSON storage setting when provided.
        @return The pyinaturalist observation response dictionary.
        """
        should_store = self._store_files if store is None else store
        if should_store and output_file_name is None:
            raise ValueError("output_file_name is required when storing observations")

        LOGGER.debug("Fetching OSA Conservation observations with per_page=%s", per_page)
        observation_response = get_observations(
            user_login=OSA_USER_LOGIN,
            per_page=per_page,
            session=self._session,
        )
        if self._session._last_response_from_cache:
            LOGGER.info("Observation data was loaded from cache")
        else:
            LOGGER.info("Observation data was downloaded from the iNaturalist API")

        if output_file_name is not None:
            saved_file_path = self._save_json_if_enabled(output_file_name, observation_response, store=store)
            if saved_file_path is None:
                LOGGER.info("Observation data was not stored in a file")
        else:
            LOGGER.info("Observation data was not stored in a file")

        return observation_response
