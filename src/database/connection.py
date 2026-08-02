"""Database connection helpers.

@file connection.py
@brief Opens PostgreSQL connections for the pipeline.
"""

import os

import psycopg
from psycopg import Connection

from .constants import DATABASE_URL_ENV_VAR


def get_database_url() -> str:
    """Get the configured PostgreSQL connection string.

    @return Database connection string.
    """
    database_url = os.environ.get(DATABASE_URL_ENV_VAR)
    if not database_url:
        raise RuntimeError(f"Missing required environment variable: {DATABASE_URL_ENV_VAR}")
    return database_url


def open_database_connection() -> Connection:
    """Open a PostgreSQL database connection.

    @return Open psycopg connection.
    """
    return psycopg.connect(get_database_url())
