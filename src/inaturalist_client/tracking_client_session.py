"""Tracking pyinaturalist session.

@file tracking_client_session.py
@brief Tracks whether the last pyinaturalist response came from cache.
"""

from pyinaturalist.session import ClientSession


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
