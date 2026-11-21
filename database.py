"""SQLite connection and schema setup."""

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
BUSY_TIMEOUT_SECONDS = 5.0


def connect(database: str | Path) -> sqlite3.Connection:
    """Open a connection with foreign keys enforced and a busy timeout."""
    connection = sqlite3.connect(database, timeout=BUSY_TIMEOUT_SECONDS)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    """Create all tables that do not exist yet."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema)
