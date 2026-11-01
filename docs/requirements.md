# Requirements

> Status: **Approved** — MVP scope agreed on 2026-10-04; revised on 2026-10-25.

## 1. Problem

Fatec professors are contacted by multiple students, through scattered WhatsApp chats, about the same issues. Even after a professor has already discussed a topic with the class representative, other students in the same class reach out about it again, forcing the professor to repeat answers.

## 2. Goal

Provide a **support tool** (not an official institutional channel) that helps professors and class representatives communicate directly, so that:

- professors answer each issue once, to the class representative;
- targeted messages have a recorded read confirmation.

## 3. Communication channels

| Need | Solution | Built by this project? |
|---|---|---|
| Notices any student can read | Native Telegram **public channel** | No |
| General notices to all class representatives | Native Telegram **group** with all class representatives | No |
| Targeted messages with read confirmation | **This bot** | Yes |

Rule of thumb: **messages sent through the bot always require acknowledgment; messages posted in the group never do.**

## 4. Users

| User | Description | Access |
|---|---|---|
| Professor | Any Fatec professor | Authenticated (access code) |
| Class representative | Student elected by the class to represent it | Authenticated (access code) |
| Vice class representative | Student elected as the representative's substitute | Authenticated (access code) |
| Other students | Any other Telegram user | Not authenticated; receives a default reply |

## 5. MVP scope

| ID | Feature |
|---|---|
| F1 | Authentication with single-use access codes |
| F2 | A professor sends a targeted message to one or more class groups |
| F3 | A class representative (or vice) sends a message to a professor chosen from a list |
| F4 | Unauthenticated users receive a default reply pointing them to their class representative and the public channel |
| F5 | Every message sent through the bot must be acknowledged; acknowledgments are stored with timestamp |

## 6. Out of scope (backlog)

- Setup guide for the public channel and the class representatives' group
- Replying directly to a professor's message as a shortcut for F3
- AI-based detection of repeated questions and automatic answers based on previous messages
- Before/after metric survey with professors
- Self-service access code generation and user deactivation (MVP: done by the developer via script)
- Student ID (RA) validation
- LGPD (Brazilian data protection law) compliance review
- Migration from SQLite to PostgreSQL

## 7. Business rules

| ID | Rule |
|---|---|
| BR-01 | The bot is a support tool, not an official institutional channel |
| BR-02 | Only authenticated professors, class representatives and vice class representatives can use F2, F3 and F5 |
| BR-03 | An access code can be used only once and is bound to the Telegram account that redeems it |
| BR-04 | A professor's message can target one or more class groups |
| BR-05 | Each class group has one class representative and one vice class representative |
| BR-06 | A message to a class group is acknowledged when **either** its class representative **or** its vice acknowledges it. Every acknowledgment is stored individually |
| BR-07 | A message from a class representative or vice to a professor is acknowledged by that professor |
| BR-08 | Acknowledgments cannot be edited or deleted |
| BR-09 | General notices to all class representatives are posted in the native group and do not require acknowledgment (presumed knowledge) |
| BR-10 | Users are deactivated, never deleted, so their acknowledgment history is preserved. A user who loses their Telegram account, or a newly elected representative, receives a new access code |

## 8. Acceptance criteria (MVP)

- **F1:** a valid unused code links the Telegram account to its role (and class group, when applicable); a used or unknown code is rejected with a clear message.
- **F2:** a professor selects the target class groups; their class representative and vice receive the message with an "Acknowledge" button.
- **F3:** a class representative or vice picks a professor from a list and sends a message; the professor receives it with an "Acknowledge" button.
- **F4:** any message from an unauthenticated user receives the default reply.
- **F5:** pressing "Acknowledge" stores who acknowledged, which message and when; the sender can check which class groups have and have not acknowledged.

## 9. Success metric

Reduction of scattered support requests to professors about the same issue. Baseline and measurement method: **to be defined** (backlog).

## 10. Glossary

| Term | Portuguese | Meaning |
|---|---|---|
| Class group | Turma | A group of students of a course and semester |
| Class representative | Líder de turma | Student elected to represent the class group |
| Vice class representative | Vice-líder | The class representative's substitute |
| Acknowledgment | Ciência / aceite | Recorded confirmation that a recipient read a message |
| Access code | Código de acesso | Single-use code that authenticates a user |
| Public channel | Canal público | Native Telegram channel for notices anyone can read |
| Representatives' group | Grupo de líderes | Native Telegram group with all class representatives, for general notices |
| Presumed knowledge | Presunção de ciência | Recipients are considered informed without acknowledgment |
