CREATE TABLE IF NOT EXISTS class_groups (
    id     INTEGER PRIMARY KEY,
    name   TEXT    NOT NULL,
    course TEXT    NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS users (
    id             INTEGER PRIMARY KEY,
    telegram_id    INTEGER NOT NULL UNIQUE,
    name           TEXT    NOT NULL,
    role           TEXT    NOT NULL
        CHECK (role IN ('professor', 'representative', 'vice_representative')),
    class_group_id INTEGER REFERENCES class_groups(id),
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
) STRICT;

CREATE TABLE IF NOT EXISTS access_codes (
    id             INTEGER PRIMARY KEY,
    code           TEXT    NOT NULL UNIQUE,
    role           TEXT    NOT NULL
        CHECK (role IN ('professor', 'representative', 'vice_representative')),
    class_group_id INTEGER REFERENCES class_groups(id),
    used_by        INTEGER UNIQUE REFERENCES users(id),
    used_at        TEXT,
    CHECK ((used_by IS NULL) = (used_at IS NULL))
) STRICT;

CREATE TABLE IF NOT EXISTS messages (
    id        INTEGER PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    text      TEXT    NOT NULL,
    sent_at   TEXT    NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS message_recipients (
    id             INTEGER PRIMARY KEY,
    message_id     INTEGER NOT NULL REFERENCES messages(id),
    class_group_id INTEGER REFERENCES class_groups(id),
    user_id        INTEGER REFERENCES users(id),
    CHECK (
        (class_group_id IS NOT NULL AND user_id IS NULL)
        OR (class_group_id IS NULL AND user_id IS NOT NULL)
    ),
    UNIQUE (message_id, class_group_id),
    UNIQUE (message_id, user_id)
) STRICT;

CREATE TABLE IF NOT EXISTS acknowledgments (
    id              INTEGER PRIMARY KEY,
    message_id      INTEGER NOT NULL REFERENCES messages(id),
    user_id         INTEGER NOT NULL REFERENCES users(id),
    acknowledged_at TEXT    NOT NULL,
    UNIQUE (message_id, user_id)
) STRICT;
