# telegram-class-notice-bot

A Python Telegram bot that helps professors reach class representatives directly, with read receipts, cutting down on repeated student questions.

> **Status: work in progress.** The MVP is under development. See [Roadmap](#roadmap) for what already works.

## The problem

At Fatec, professors are contacted by many students, through scattered WhatsApp chats, about the same issues. Even after a professor has discussed a topic with the class representative, other students ask again, and the professor has to repeat the answer.

## How it works

The solution combines native Telegram features with a bot, each used where it fits best:

| Need | Solution |
|---|---|
| Notices any student can read | Telegram public channel |
| General notices to all class representatives | Telegram group |
| Targeted messages that need a read receipt | **This bot** |

Every message sent through the bot must be acknowledged by its recipient, and each acknowledgment is stored with a timestamp.

> This is a student support tool, not an official Fatec channel.

## Roadmap

- [x] Bot responds to `/start`
- [x] Startup validation of the bot token
- [ ] Authentication with single-use access codes
- [ ] Targeted messages from professors to one or more class groups
- [ ] Messages from class representatives to professors
- [ ] Default reply for unauthenticated users
- [ ] Acknowledgment tracking

## Tech stack

- Python 3.13
- [python-telegram-bot](https://python-telegram-bot.org/)
- SQLite (MVP)

## Getting started

### Prerequisites

- Python 3.13
- A Telegram bot token, created with [@BotFather](https://t.me/BotFather)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/DiegoCP89/telegram-class-notice-bot.git
cd telegram-class-notice-bot

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
source venv/Scripts/activate    # Windows (Git Bash)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your bot token
cp .env.example .env
# then edit .env and set TELEGRAM_BOT_TOKEN

# 5. Run the bot
python main.py
```

## Documentation

- [Requirements](docs/requirements.md)
- [Data model](docs/data-model.md)
- [Architecture decision records](docs/adr/)

## License

[MIT](LICENSE)
