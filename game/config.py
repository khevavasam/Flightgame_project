"""
config.py
=========
Loads environment variables and exposes project-level configuration.

Environment variables:
    DB_USER: Database username.
    DB_PASSWORD: Database password.
    DB_HOST: Database host address (default: 127.0.0.1).
    DB_PORT: Database port number (default: 3306).
    DB_NAME: Database name (default: flight_game).
"""

from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_NAME = os.getenv("DB_NAME", "flight_game")
