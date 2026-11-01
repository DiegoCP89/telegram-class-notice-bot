# ADR-0002: Use native Telegram features for general notices

- **Status:** Accepted
- **Date:** 2026-10-25

## Context

The bot is a support tool, not an official institutional channel (BR-01). Messages fall into two groups with different needs:

- **General notices** for everyone, which do not need proof of reading.
- **Targeted messages** to specific class groups or professors, which need a recorded acknowledgment.

Sending general notices through the bot would either force acknowledgments where they add no value (each class group has a representative and a vice, so every general notice would generate many pending acknowledgments) or create a second, inconsistent rule inside the bot.

## Decision

- Notices any student can read go to a native Telegram **public channel**.
- General notices for all class representatives go to a native Telegram **group** with all class representatives.
- The **bot** handles only targeted messages, and every message sent through the bot requires acknowledgment.

Rule of thumb: **through the bot, always acknowledgment; in the group, never.**

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Bot sends general notices **with** acknowledgment | Adds friction to messages that do not need proof of reading; may hurt adoption of a support tool |
| Bot sends general notices **without** acknowledgment | Creates two rules inside the bot and duplicates what Telegram groups already do |
| Bot handles every kind of communication | Larger scope and more code to build, test and maintain |

## Consequences

**Positive**

- Smaller bot: less code to build, test and maintain.
- A simple, consistent rule: every bot message requires acknowledgment.
- Channels and groups are free, reliable and already familiar to Telegram users.

**Negative**

- General notices have no recorded proof of reading (presumed knowledge, BR-09).
- Communication is split across three places; users must know where to look.
- The channel and the group are configured manually, outside the codebase.

## When to revisit

If class representatives often claim they were unaware of general notices posted in the group.
