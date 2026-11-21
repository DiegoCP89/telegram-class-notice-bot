"""SQLite connection and schema setup."""

import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import cast

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


def create_message(
    connection: sqlite3.Connection,
    sender_id: int,
    text: str,
    sent_at: str,
    class_group_ids: Sequence[int] = (),
    user_ids: Sequence[int] = (),
) -> int:
    """Save a message and its recipients atomically and return the message id."""
    if not class_group_ids and not user_ids:
        raise ValueError("A message needs at least one recipient.")

    with connection:
        cursor = connection.execute(
            "INSERT INTO messages (sender_id, text, sent_at) VALUES (?, ?, ?)",
            (sender_id, text, sent_at),
        )
        message_id = cast(int, cursor.lastrowid)
        recipients: list[tuple[int, int | None, int | None]] = [
            (message_id, class_group_id, None) for class_group_id in class_group_ids
        ]
        recipients += [(message_id, None, user_id) for user_id in user_ids]
        connection.executemany(
            "INSERT INTO message_recipients (message_id, class_group_id, user_id) "
            "VALUES (?, ?, ?)",
            recipients,
        )
    return message_id
