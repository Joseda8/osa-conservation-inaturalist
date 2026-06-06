"""Database connection helpers.

@file connection.py
@brief Opens PostgreSQL connections for the pipeline.
"""

import os

import psycopg
from psycopg import Connection

from .constants import DATABASE_URL_ENV_VAR, DEFAULT_DATABASE_URL


def get_database_url() -> str:
    """Get the configured PostgreSQL connection string.

    @return Database connection string.
    """
    return os.environ.get(DATABASE_URL_ENV_VAR, DEFAULT_DATABASE_URL)


def open_database_connection() -> Connection:
    """Open a PostgreSQL database connection.

    @return Open psycopg connection.
    """
    return psycopg.connect(get_database_url())
