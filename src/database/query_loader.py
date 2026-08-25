"""SQL query file loader.

@file query_loader.py
@brief Reads and caches SQL query files executed by the database layer.
"""

from functools import cache
from pathlib import Path


@cache
def load_sql_query(query_path: Path) -> str:
    """Read one SQL query file once per process.

    @param query_path SQL file to load.
    @return SQL query text.
    """
    return query_path.read_text()
