# ADR-0003: Authenticate users with single-use access codes

- **Status:** Accepted
- **Date:** 2026-10-04

## Context

Only professors, class representatives and vice class representatives may use the bot's features (BR-02). The bot receives each user's Telegram ID, but it has no way to know whether that person is a professor or which class group they represent. Asking users to declare their own role would let any student claim to be a professor. The bot has no access to Fatec's academic systems.

## Decision

The administrator generates an **access code** for each user, stating the role and, for representatives, the class group. The user sends the code to the bot once:

- a valid, unused code creates the user with the code's role and class group, bound to the sender's Telegram ID, and the code is marked as used;
- a used or unknown code is rejected with a clear message.

After that, the bot recognizes the user by their Telegram ID.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Self-declared role | Anyone could claim to be a professor |
| Shared password per role | Easily passed around; impossible to tell who leaked it |
| Validation against Fatec's academic system (student ID) | No access to the system; out of MVP scope |

## Consequences

**Positive**

- Simple to build and explain; no external dependencies.
- A shared code works only once, so leaks are visible.

**Negative**

- Manual work for the administrator: generating, delivering and tracking codes (MVP: via script).
- A user who loses their Telegram account needs a new code (BR-10).

## When to revisit

If the number of users grows beyond what an administrator can handle manually, or if Fatec offers an official authentication service.
