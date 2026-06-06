"""Colored log formatter.

@file colored_formatter.py
@brief Formats log messages with colors by level.
"""

import logging


class ColoredFormatter(logging.Formatter):
    """Formatter that colors log messages based on their level."""

    # ANSI color for DEBUG messages.
    _DEBUG_COLOR = "\033[32m"

    # ANSI color for INFO messages.
    _INFO_COLOR = "\033[34m"

    # ANSI color for WARNING messages.
    _WARNING_COLOR = "\033[33m"

    # ANSI color for ERROR and CRITICAL messages.
    _ERROR_COLOR = "\033[31m"

    # ANSI reset sequence.
    _RESET_COLOR = "\033[0m"

    # Mapping between logging levels and ANSI colors.
    _LEVEL_COLORS = {
        logging.DEBUG: _DEBUG_COLOR,
        logging.INFO: _INFO_COLOR,
        logging.WARNING: _WARNING_COLOR,
        logging.ERROR: _ERROR_COLOR,
        logging.CRITICAL: _ERROR_COLOR,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with a level-specific color.

        @param record Log record to format.
        @return Colored log message.
        """
        message = super().format(record)
        color = self._LEVEL_COLORS.get(record.levelno, self._RESET_COLOR)
        return f"{color}{message}{self._RESET_COLOR}"
