# ADR-0005: Use SQLite for the MVP

- **Status:** Accepted
- **Date:** 2026-11-01

## Context

The bot must store users, access codes, messages and acknowledgments, and acknowledgments must survive restarts to serve as proof (BR-08). The MVP runs with few users and low traffic.

## Decision

Use **SQLite** in the MVP, with the database stored in a single file.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| PostgreSQL from the start | Requires installing and running a database server; more setup before any feature exists |
| In-memory storage | Data is lost on every restart; acknowledgments would no longer be proof |

## Consequences

**Positive**

- No server to install: SQLite ships with Python.
- Supports the constraints the data model needs (`UNIQUE`, `CHECK`, foreign keys).

**Negative**

- Limited for concurrent writes; fine for the MVP, not for heavy usage.
- Many hosting platforms use temporary disks, so the database file may be lost on redeploy.
- A future migration to PostgreSQL will require work (listed in the backlog).

## When to revisit

Before deploy, if the hosting platform does not provide persistent disk storage, or if usage grows beyond a few dozen active users.
