# ADR-0001: Use Telegram as the platform

- **Status:** Accepted
- **Date:** 2026-10-04

## Context

Professors and students at Fatec already communicate through WhatsApp, in scattered chats. The project needs a messaging platform where a bot can authenticate users, send targeted messages and record acknowledgments.

## Decision

Build the bot on **Telegram**, using the official Telegram Bot API.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| WhatsApp Business Platform (official API) | Requires business verification by Meta and has usage-based costs; heavy for a student support tool |
| Unofficial WhatsApp APIs | Not supported by Meta; risk of account bans and breaking changes |
| Custom web or mobile app | Users would need to install and learn a new app; much larger scope |

## Consequences

**Positive**

- The Bot API is free, official and well documented.
- Native features (public channels, groups, inline buttons) cover part of the scope without custom code (see ADR-0002).

**Negative**

- Adoption risk: professors and class representatives must install and use Telegram, while most of them already live on WhatsApp.

## When to revisit

If adoption stays low after a pilot, or if the institution provides an official messaging platform with an API.
