"""File storage helpers for downloaded data.

@file storage.py
@brief Provides reusable JSON storage behavior for downloader classes.
"""

import json
from pathlib import Path
from typing import Any

from utils import LOGGER


class JsonFileStorage:
    """Base class for writing downloaded data to JSON files.

    @param storage_dir Directory where JSON files are written.
    @param store_files Whether downloads should be saved by default.
    """

    def __init__(self, storage_dir: Path | str, store_files: bool = True):
        """Create a JSON file storage helper.

        @param storage_dir Directory where JSON files are written.
        @param store_files Whether downloads should be saved by default.
        """
        self._storage_dir = Path(storage_dir)
        self._store_files = store_files

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

    def _save_json_if_enabled(self, file_path: Path | str, content: Any, store: bool | None = None) -> Path | None:
        """Write JSON content when storage is enabled.

        @param file_path Relative path of the JSON file to create.
        @param content JSON-serializable content to write.
        @param store Overrides the default storage setting when provided.
        @return Path to the saved file, or None when storage is disabled.
        """
        should_store = self._store_files if store is None else store
        if not should_store:
            return None

        return self._save_json(file_path, content)
