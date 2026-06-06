"""Logging helpers.

@file logger.py
@brief Provides the shared project logger instance.
"""

from .project_logger import ProjectLogger


# Shared project logger.
LOGGER = ProjectLogger.get_instance()
