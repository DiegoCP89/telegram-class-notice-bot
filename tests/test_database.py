"""Tests for the SQLite connection setup and schema constraints."""

import re
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta, timezone

import pytest

import database

SqlValue = int | str | None

NOW = "2026-11-21T14:30:00+00:00"
SENT_AT = datetime(2026, 11, 21, 14, 30, tzinfo=UTC)
MISSING_ID = 999
FOREIGN_KEY_ERROR = "FOREIGN KEY constraint failed"
RECIPIENT_CHECK_ERROR = "CHECK constraint failed"
ROLE_CLASS_GROUP_ERROR = (
    "CHECK constraint failed: (role = 'professor') = (class_group_id IS NULL)"
)

INSERT_CLASS_GROUP = "INSERT INTO class_groups (name, course) VALUES (?, ?)"
INSERT_USER = (
    "INSERT INTO users (telegram_id, name, role, class_group_id, is_active) "
    "VALUES (?, ?, ?, ?, ?)"
)
INSERT_CODE = (
    "INSERT INTO access_codes (code, role, class_group_id, used_by, used_at) "
    "VALUES (?, ?, ?, ?, ?)"
)
INSERT_MESSAGE = "INSERT INTO messages (sender_id, text, sent_at) VALUES (?, ?, ?)"
INSERT_RECIPIENT = (
    "INSERT INTO message_recipients (message_id, class_group_id, user_id) "
    "VALUES (?, ?, ?)"
)
INSERT_ACK = (
    "INSERT INTO acknowledgments (message_id, user_id, acknowledged_at) "
    "VALUES (?, ?, ?)"
)


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    """Provide an in-memory database with one valid row set per table."""
    conn = database.connect(":memory:")
    database.create_schema(conn)
    with conn:
        conn.execute(INSERT_CLASS_GROUP, ("Group A", "ADS"))
        conn.execute(INSERT_USER, (101, "Ana", "professor", None, 1))
        conn.execute(INSERT_USER, (102, "Bruno", "representative", 1, 1))
        conn.execute(INSERT_USER, (103, "Carla", "vice_representative", 1, 1))
        conn.execute(INSERT_MESSAGE, (1, "Exam tomorrow", NOW))
        conn.execute(INSERT_MESSAGE, (1, "Class canceled", NOW))
        conn.execute(INSERT_RECIPIENT, (1, 1, None))
        conn.execute(INSERT_RECIPIENT, (2, None, 2))
        conn.execute(INSERT_ACK, (1, 2, NOW))
        conn.execute(INSERT_CODE, ("USED01", "professor", None, 1, NOW))
        conn.execute(INSERT_CODE, ("FREE01", "representative", 1, None, None))
    yield conn
    conn.close()


def test_connect_enables_foreign_keys() -> None:
    conn = database.connect(":memory:")
    try:
        assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
    finally:
        conn.close()


def test_create_schema_is_idempotent(connection: sqlite3.Connection) -> None:
    database.create_schema(connection)

    assert connection.execute("SELECT COUNT(*) FROM users").fetchone() == (3,)


@pytest.mark.parametrize(
    ("sql", "values", "expected_error"),
    [
        pytest.param(
            INSERT_CLASS_GROUP,
            (None, "ADS"),
            "NOT NULL constraint failed: class_groups.name",
            id="class_group_without_name",
        ),
        pytest.param(
            INSERT_CLASS_GROUP,
            ("Group B", None),
            "NOT NULL constraint failed: class_groups.course",
            id="class_group_without_course",
        ),
        pytest.param(
            INSERT_USER,
            (None, "Davi", "professor", None, 1),
            "NOT NULL constraint failed: users.telegram_id",
            id="user_without_telegram_id",
        ),
        pytest.param(
            INSERT_USER,
            (101, "Davi", "professor", None, 1),
            "UNIQUE constraint failed: users.telegram_id",
            id="user_duplicate_telegram_id",
        ),
        pytest.param(
            INSERT_USER,
            ("abc", "Davi", "professor", None, 1),
            "cannot store TEXT value in INTEGER column users.telegram_id",
            id="user_text_telegram_id",
        ),
        pytest.param(
            INSERT_USER,
            (104, None, "professor", None, 1),
            "NOT NULL constraint failed: users.name",
            id="user_without_name",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", None, None, 1),
            "NOT NULL constraint failed: users.role",
            id="user_without_role",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "student", 1, 1),
            "CHECK constraint failed: role IN",
            id="user_invalid_role",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "representative", MISSING_ID, 1),
            FOREIGN_KEY_ERROR,
            id="user_missing_class_group",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "professor", None, None),
            "NOT NULL constraint failed: users.is_active",
            id="user_without_is_active",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "professor", None, 2),
            "CHECK constraint failed: is_active IN (0, 1)",
            id="user_invalid_is_active",
        ),
        pytest.param(
            INSERT_CODE,
            (None, "professor", None, None, None),
            "NOT NULL constraint failed: access_codes.code",
            id="code_without_value",
        ),
        pytest.param(
            INSERT_CODE,
            ("FREE01", "professor", None, None, None),
            "UNIQUE constraint failed: access_codes.code",
            id="code_duplicate_value",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", None, None, None, None),
            "NOT NULL constraint failed: access_codes.role",
            id="code_without_role",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "student", 1, None, None),
            "CHECK constraint failed: role IN",
            id="code_invalid_role",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "representative", MISSING_ID, None, None),
            FOREIGN_KEY_ERROR,
            id="code_missing_class_group",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "professor", None, MISSING_ID, NOW),
            FOREIGN_KEY_ERROR,
            id="code_missing_user",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "professor", None, 2, None),
            "CHECK constraint failed: (used_by IS NULL) = (used_at IS NULL)",
            id="code_used_by_without_used_at",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "professor", None, None, NOW),
            "CHECK constraint failed: (used_by IS NULL) = (used_at IS NULL)",
            id="code_used_at_without_used_by",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "professor", None, 1, NOW),
            "UNIQUE constraint failed: access_codes.used_by",
            id="code_user_redeems_twice",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "representative", 1, 1),
            "UNIQUE constraint failed: users.class_group_id, users.role",
            id="user_second_active_representative",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "vice_representative", 1, 1),
            "UNIQUE constraint failed: users.class_group_id, users.role",
            id="user_second_active_vice",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "representative", None, 1),
            ROLE_CLASS_GROUP_ERROR,
            id="user_representative_without_class_group",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "vice_representative", None, 1),
            ROLE_CLASS_GROUP_ERROR,
            id="user_vice_without_class_group",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "professor", 1, 1),
            ROLE_CLASS_GROUP_ERROR,
            id="user_professor_with_class_group",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "representative", None, None, None),
            ROLE_CLASS_GROUP_ERROR,
            id="code_representative_without_class_group",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "vice_representative", None, None, None),
            ROLE_CLASS_GROUP_ERROR,
            id="code_vice_without_class_group",
        ),
        pytest.param(
            INSERT_CODE,
            ("NEW001", "professor", 1, None, None),
            ROLE_CLASS_GROUP_ERROR,
            id="code_professor_with_class_group",
        ),
        pytest.param(
            INSERT_MESSAGE,
            (None, "Text", NOW),
            "NOT NULL constraint failed: messages.sender_id",
            id="message_without_sender",
        ),
        pytest.param(
            INSERT_MESSAGE,
            (MISSING_ID, "Text", NOW),
            FOREIGN_KEY_ERROR,
            id="message_missing_sender",
        ),
        pytest.param(
            INSERT_MESSAGE,
            (1, None, NOW),
            "NOT NULL constraint failed: messages.text",
            id="message_without_text",
        ),
        pytest.param(
            INSERT_MESSAGE,
            (1, "Text", None),
            "NOT NULL constraint failed: messages.sent_at",
            id="message_without_sent_at",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (None, 1, None),
            "NOT NULL constraint failed: message_recipients.message_id",
            id="recipient_without_message",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (MISSING_ID, 1, None),
            FOREIGN_KEY_ERROR,
            id="recipient_missing_message",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (2, MISSING_ID, None),
            FOREIGN_KEY_ERROR,
            id="recipient_missing_class_group",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (1, None, MISSING_ID),
            FOREIGN_KEY_ERROR,
            id="recipient_missing_user",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (2, 1, 1),
            RECIPIENT_CHECK_ERROR,
            id="recipient_with_group_and_user",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (2, None, None),
            RECIPIENT_CHECK_ERROR,
            id="recipient_without_group_or_user",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (1, 1, None),
            "UNIQUE constraint failed: "
            "message_recipients.message_id, message_recipients.class_group_id",
            id="recipient_duplicate_class_group",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (2, None, 2),
            "UNIQUE constraint failed: "
            "message_recipients.message_id, message_recipients.user_id",
            id="recipient_duplicate_user",
        ),
        pytest.param(
            INSERT_ACK,
            (None, 2, NOW),
            "NOT NULL constraint failed: acknowledgments.message_id",
            id="ack_without_message",
        ),
        pytest.param(
            INSERT_ACK,
            (2, None, NOW),
            "NOT NULL constraint failed: acknowledgments.user_id",
            id="ack_without_user",
        ),
        pytest.param(
            INSERT_ACK,
            (2, 2, None),
            "NOT NULL constraint failed: acknowledgments.acknowledged_at",
            id="ack_without_timestamp",
        ),
        pytest.param(
            INSERT_ACK,
            (MISSING_ID, 2, NOW),
            FOREIGN_KEY_ERROR,
            id="ack_missing_message",
        ),
        pytest.param(
            INSERT_ACK,
            (2, MISSING_ID, NOW),
            FOREIGN_KEY_ERROR,
            id="ack_missing_user",
        ),
        pytest.param(
            INSERT_ACK,
            (1, 2, NOW),
            "UNIQUE constraint failed: "
            "acknowledgments.message_id, acknowledgments.user_id",
            id="ack_duplicate",
        ),
    ],
)
def test_constraint_rejects_invalid_data(
    connection: sqlite3.Connection,
    sql: str,
    values: tuple[SqlValue, ...],
    expected_error: str,
) -> None:
    with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected_error)):
        connection.execute(sql, values)


@pytest.mark.parametrize(
    ("sql", "values"),
    [
        pytest.param(
            INSERT_USER,
            (104, "Davi", "professor", None, 1),
            id="professor_without_class_group",
        ),
        pytest.param(
            INSERT_USER,
            (101, "Ana", "professor", None, 0),
            id="inactive_user_reuses_telegram_id",
        ),
        pytest.param(
            INSERT_USER,
            (104, "Davi", "representative", 1, 0),
            id="inactive_user_does_not_fill_role",
        ),
        pytest.param(
            INSERT_CODE,
            ("FREE02", "representative", 1, None, None),
            id="second_unused_code",
        ),
        pytest.param(
            INSERT_CODE,
            ("USED02", "representative", 1, 2, NOW),
            id="redeemed_code",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (2, 1, None),
            id="recipient_class_group_only",
        ),
        pytest.param(
            INSERT_RECIPIENT,
            (1, None, 1),
            id="recipient_user_only",
        ),
        pytest.param(
            INSERT_ACK,
            (2, 2, NOW),
            id="same_user_acknowledges_another_message",
        ),
        pytest.param(
            INSERT_ACK,
            (1, 3, NOW),
            id="another_user_acknowledges_same_message",
        ),
    ],
)
def test_schema_accepts_valid_data(
    connection: sqlite3.Connection,
    sql: str,
    values: tuple[SqlValue, ...],
) -> None:
    cursor = connection.execute(sql, values)

    assert cursor.rowcount == 1


@pytest.mark.parametrize(
    ("sql", "expected_error"),
    [
        pytest.param(
            "UPDATE acknowledgments SET acknowledged_at = 'forged'",
            "Acknowledgments cannot be changed.",
            id="update_acknowledgment",
        ),
        pytest.param(
            "DELETE FROM acknowledgments",
            "Acknowledgments cannot be deleted.",
            id="delete_acknowledgment",
        ),
        pytest.param(
            "UPDATE access_codes SET used_by = 2 WHERE code = 'USED01'",
            "Redeemed access codes cannot be changed.",
            id="transfer_redeemed_code",
        ),
        pytest.param(
            "DELETE FROM access_codes WHERE code = 'USED01'",
            "Redeemed access codes cannot be deleted.",
            id="delete_redeemed_code",
        ),
    ],
)
def test_trigger_blocks_protected_change(
    connection: sqlite3.Connection, sql: str, expected_error: str
) -> None:
    with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected_error)):
        connection.execute(sql)


def test_unused_code_can_be_redeemed(connection: sqlite3.Connection) -> None:
    cursor = connection.execute(
        "UPDATE access_codes SET used_by = 2, used_at = ? WHERE code = 'FREE01'",
        (NOW,),
    )

    assert cursor.rowcount == 1


def test_deactivated_user_can_return_with_new_code(
    connection: sqlite3.Connection,
) -> None:
    with connection:
        connection.execute("UPDATE users SET is_active = 0 WHERE id IN (2, 3)")
        cursor = connection.execute(INSERT_USER, (103, "Carla", "representative", 1, 1))
        connection.execute(
            "UPDATE access_codes SET used_by = ?, used_at = ? WHERE code = 'FREE01'",
            (cursor.lastrowid, NOW),
        )

    assert connection.execute(
        "SELECT COUNT(*) FROM users WHERE telegram_id = 103"
    ).fetchone() == (2,)
    assert connection.execute(
        "SELECT COUNT(*) FROM acknowledgments WHERE user_id = 2"
    ).fetchone() == (1,)


def count_messages_and_recipients(connection: sqlite3.Connection) -> tuple[int, int]:
    """Return the number of rows in messages and message_recipients."""
    row = connection.execute(
        "SELECT (SELECT COUNT(*) FROM messages), "
        "(SELECT COUNT(*) FROM message_recipients)"
    ).fetchone()
    return int(row[0]), int(row[1])


def test_create_message_saves_class_group_recipients(
    connection: sqlite3.Connection,
) -> None:
    with connection:
        connection.execute(INSERT_CLASS_GROUP, ("Group B", "ADS"))

    message_id = database.create_message(
        connection, 1, "Exam moved", SENT_AT, class_group_ids=[1, 2]
    )

    assert connection.execute(
        "SELECT sender_id, text, sent_at FROM messages WHERE id = ?", (message_id,)
    ).fetchone() == (1, "Exam moved", NOW)
    assert connection.execute(
        "SELECT class_group_id, user_id FROM message_recipients "
        "WHERE message_id = ? ORDER BY class_group_id",
        (message_id,),
    ).fetchall() == [(1, None), (2, None)]


def test_create_message_saves_user_recipient(connection: sqlite3.Connection) -> None:
    message_id = database.create_message(
        connection, 2, "Question about the exam", SENT_AT, user_ids=[1]
    )

    assert connection.execute(
        "SELECT class_group_id, user_id FROM message_recipients WHERE message_id = ?",
        (message_id,),
    ).fetchall() == [(None, 1)]


def test_create_message_requires_a_recipient(connection: sqlite3.Connection) -> None:
    before = count_messages_and_recipients(connection)

    with pytest.raises(ValueError, match="at least one recipient"):
        database.create_message(connection, 1, "No recipient", SENT_AT)

    assert count_messages_and_recipients(connection) == before


@pytest.mark.parametrize(
    ("sender_id", "class_group_ids", "expected_error"),
    [
        pytest.param(MISSING_ID, [1], FOREIGN_KEY_ERROR, id="missing_sender"),
        pytest.param(1, [1, MISSING_ID], FOREIGN_KEY_ERROR, id="missing_class_group"),
        pytest.param(
            1,
            [1, 1],
            "UNIQUE constraint failed: "
            "message_recipients.message_id, message_recipients.class_group_id",
            id="duplicate_class_group",
        ),
    ],
)
def test_create_message_failure_leaves_no_partial_data(
    connection: sqlite3.Connection,
    sender_id: int,
    class_group_ids: list[int],
    expected_error: str,
) -> None:
    before = count_messages_and_recipients(connection)

    with pytest.raises(sqlite3.IntegrityError, match=re.escape(expected_error)):
        database.create_message(
            connection, sender_id, "Partial", SENT_AT, class_group_ids=class_group_ids
        )

    assert count_messages_and_recipients(connection) == before


def test_create_message_stores_sent_at_in_utc(connection: sqlite3.Connection) -> None:
    local_time = datetime(2026, 11, 21, 11, 30, tzinfo=timezone(timedelta(hours=-3)))

    message_id = database.create_message(
        connection, 1, "Exam moved", local_time, class_group_ids=[1]
    )

    assert connection.execute(
        "SELECT sent_at FROM messages WHERE id = ?", (message_id,)
    ).fetchone() == (NOW,)


def test_create_message_rejects_sent_at_without_time_zone(
    connection: sqlite3.Connection,
) -> None:
    before = count_messages_and_recipients(connection)

    with pytest.raises(ValueError, match="time zone"):
        database.create_message(
            connection,
            1,
            "No time zone",
            datetime(2026, 11, 21, 14, 30),
            class_group_ids=[1],
        )

    assert count_messages_and_recipients(connection) == before


def test_create_message_does_not_commit_caller_transaction(
    connection: sqlite3.Connection,
) -> None:
    connection.execute(INSERT_CLASS_GROUP, ("Group B", "ADS"))

    with pytest.raises(RuntimeError, match="open transaction"):
        database.create_message(connection, 1, "Inside", SENT_AT, class_group_ids=[1])
    connection.rollback()

    assert connection.execute("SELECT COUNT(*) FROM class_groups").fetchone() == (1,)


def test_create_schema_does_not_commit_caller_transaction(
    connection: sqlite3.Connection,
) -> None:
    connection.execute(INSERT_CLASS_GROUP, ("Group B", "ADS"))

    with pytest.raises(RuntimeError, match="open transaction"):
        database.create_schema(connection)
    connection.rollback()

    assert connection.execute("SELECT COUNT(*) FROM class_groups").fetchone() == (1,)
