"""Project logger singleton.

@file project_logger.py
@brief Creates the shared project logger.
"""

import logging

from .colored_formatter import ColoredFormatter


class ProjectLogger:
    """Singleton factory for the project logger."""

    _instance: logging.Logger | None = None

    @classmethod
    def get_instance(cls) -> logging.Logger:
        """Get the shared project logger.

        @return Shared project logger.
        """
        if cls._instance is None:
            cls._instance = logging.getLogger("osa_inaturalist")
            cls._instance.setLevel(logging.DEBUG)
            cls._instance.propagate = False
            cls._instance.addHandler(cls._create_console_handler())

        return cls._instance

    @classmethod
    def _create_console_handler(cls) -> logging.StreamHandler:
        """Create the colored console log handler.

        @return Console handler with colored log formatting.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
        return console_handler
