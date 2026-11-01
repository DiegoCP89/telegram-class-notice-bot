# ADR-0004: Use the python-telegram-bot library

- **Status:** Accepted
- **Date:** 2026-10-12

## Context

The bot is written in Python. Calling the Telegram Bot API directly over HTTP would require handling updates, retries and message formatting by hand. The developer is building a Telegram bot for the first time, so documentation and examples matter.

## Decision

Use **python-telegram-bot** as the Telegram client library.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| aiogram | Solid and popular, but introduces more concepts up front and has less beginner material |
| Raw HTTP calls to the Bot API | Reimplements what mature libraries already provide |

## Consequences

**Positive**

- Widely used, with extensive documentation and ready-made examples.
- Built-in support for commands, inline buttons and callback queries, which the MVP needs.

**Negative**

- The library is asynchronous (`async`/`await`), a concept the developer is still learning.
- The project depends on a third-party library's release cycle.

## When to revisit

If the library stops being maintained, or if the bot needs features it does not support.
