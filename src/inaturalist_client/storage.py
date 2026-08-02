"""File storage helpers for downloaded data.

@file storage.py
@brief Provides reusable JSON storage behavior for downloader classes.
"""

import json
from pathlib import Path
from typing import Any

from utils import LOGGER

from .constants import DEFAULT_STORE_FILES


class JsonFileStorage:
    """Base class for writing downloaded data to JSON files.

    @param storage_dir Directory where JSON files are written.
    """

    def __init__(self, storage_dir: Path | str):
        """Create a JSON file storage helper.

        @param storage_dir Directory where JSON files are written.
        """
        self._storage_dir = Path(storage_dir)

    def _save_json(self, file_path: Path | str, content: Any) -> Path:
        """Write content to a JSON file.

        @param file_path Relative path of the JSON file to create.
        @param content JSON-serializable content to write.
        @return Path to the saved JSON file.
        """
        output_path = self._storage_dir / file_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        LOGGER.debug("Saving JSON file: %s", output_path)
        with open(output_path, "w") as output_file:
            json.dump(content, output_file, indent=2, default=str)

        LOGGER.info("Stored JSON data in file: %s", output_path)
        return output_path

    def _save_json_if_enabled(self, file_path: Path | str, content: Any, store: bool = DEFAULT_STORE_FILES) -> Path | None:
        """Write JSON content when storage is enabled.

        @param file_path Relative path of the JSON file to create.
        @param content JSON-serializable content to write.
        @param store Whether to write the content to a JSON file.
        @return Path to the saved file, or None when storage is disabled.
        """
        if not store:
            return None

        return self._save_json(file_path, content)
