CREATE TABLE IF NOT EXISTS class_groups (
    id     INTEGER PRIMARY KEY,
    name   TEXT    NOT NULL,
    course TEXT    NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS users (
    id             INTEGER PRIMARY KEY,
    telegram_id    INTEGER NOT NULL,
    name           TEXT    NOT NULL,
    role           TEXT    NOT NULL
        CHECK (role IN ('professor', 'representative', 'vice_representative')),
    class_group_id INTEGER REFERENCES class_groups(id),
    is_active      INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    CHECK ((role = 'professor') = (class_group_id IS NULL))
) STRICT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_active_telegram_id
    ON users (telegram_id)
    WHERE is_active = 1;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_active_class_group_role
    ON users (class_group_id, role)
    WHERE is_active = 1 AND class_group_id IS NOT NULL;

CREATE TRIGGER IF NOT EXISTS trg_users_block_delete
BEFORE DELETE ON users
BEGIN
    SELECT RAISE(ABORT, 'Users cannot be deleted. Deactivate them instead.');
END;

CREATE TABLE IF NOT EXISTS access_codes (
    id             INTEGER PRIMARY KEY,
    code           TEXT    NOT NULL UNIQUE,
    role           TEXT    NOT NULL
        CHECK (role IN ('professor', 'representative', 'vice_representative')),
    class_group_id INTEGER REFERENCES class_groups(id),
    used_by        INTEGER UNIQUE REFERENCES users(id),
    used_at        TEXT,
    CHECK ((used_by IS NULL) = (used_at IS NULL)),
    CHECK ((role = 'professor') = (class_group_id IS NULL))
) STRICT;

CREATE TRIGGER IF NOT EXISTS trg_access_codes_block_redeemed_update
BEFORE UPDATE ON access_codes
WHEN OLD.used_by IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'Redeemed access codes cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS trg_access_codes_block_redeemed_delete
BEFORE DELETE ON access_codes
WHEN OLD.used_by IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'Redeemed access codes cannot be deleted.');
END;

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

CREATE TRIGGER IF NOT EXISTS trg_acknowledgments_block_update
BEFORE UPDATE ON acknowledgments
BEGIN
    SELECT RAISE(ABORT, 'Acknowledgments cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS trg_acknowledgments_block_delete
BEFORE DELETE ON acknowledgments
BEGIN
    SELECT RAISE(ABORT, 'Acknowledgments cannot be deleted.');
END;
