"""
db/config.py
============
Database configuration and connection management.

Populates DB_CONFIG from environment variables and provides automatically closed
database connection via context manager.
"""

import mysql.connector
from contextlib import contextmanager
from game import config

DB_CONFIG = {
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
    "host": config.DB_HOST,
    "port": config.DB_PORT,
    "database": config.DB_NAME,
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": True,
}


@contextmanager
def get_connection():
    """
    Context manager for MySQL/MariaDB database connection.

    Yields:
        mysql.connector.connection.MySQLConnection: Database connection.
    """
    connection = mysql.connector.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()
