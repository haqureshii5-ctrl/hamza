# Binance Crypto Trend Posting Bot

A fully automated Python bot for tracking crypto trend signals, generating AI-powered social content, and posting to Twitter/X and Telegram.

## What this project includes

- Modular architecture with fetchers, analysis, AI generation, posting, and scheduling
- Trend sources: Binance Square, CoinMarketCap, CryptoPanic, Twitter/X trends, Reddit crypto communities
- OpenAI-powered post generation with hashtags, emojis, and clickbait hooks
- Duplicate detection and SQLite history storage
- Daily scheduling with APScheduler
- Docker-ready deployment

## Folder structure

- `bot/`: core bot framework
  - `config.py`: environment configuration
  - `logger.py`: central logging
  - `storage.py`: SQLite persistence for posted topics
  - `fetchers/`: source-specific trend collectors
  - `analyzer.py`: sentiment and scoring
  - `generator.py`: OpenAI prompt-based copy generation
  - `poster.py`: Twitter/X and Telegram publishers
  - `scheduler.py`: daily cron-like scheduler
- `scripts/`: runtime helpers
  - `run_bot.py`: start the scheduler or run a one-shot cycle
  - `migrate_db.py`: create database schema
- `.env.example`: example environment variables
- `Dockerfile`: container setup
- `requirements.txt`: Python dependencies

## Setup Instructions

1. Clone the repository or copy files to your VPS.
2. Copy the environment example:

```bash
cp .env.example .env
```

3. Fill in required API keys in `.env`:
- `OPENAI_API_KEY`
- `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- Optional: `CRYPTOPANIC_API_KEY`

4. Install dependencies:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

5. Initialize the database:

```bash
python scripts/migrate_db.py
```

6. Run the bot once for testing:

```bash
python scripts/run_bot.py --once
```

7. Start the daily scheduler:

```bash
python scripts/run_bot.py
```

## Docker Deployment

Build the container:

```bash
docker build -t crypto-trend-bot .
```

Run the container:

```bash
docker run --env-file .env --name crypto-trend-bot crypto-trend-bot
```

## Deployment on a VPS

1. Install Docker or Python 3.12+.
2. Copy the repository and create `.env` from `.env.example`.
3. If using Docker, build and run the image as above.
4. If using Python directly, run:

```bash
python3 -m pip install -r requirements.txt
python scripts/migrate_db.py
nohup python scripts/run_bot.py > bot.log 2>&1 &
```

5. Optionally configure a process manager like `systemd` or `supervisord`.

## How each module works

- `bot/config.py`: loads environment values and defaults with Pydantic.
- `bot/logger.py`: configures rotating logs and console output.
- `bot/storage.py`: keeps posted trends in SQLite to prevent duplicates.
- `bot/fetchers/`: collects candidate trends from multiple crypto sources.
- `bot/analyzer.py`: assigns sentiment and a normalized virality score.
- `bot/generator.py`: sends trend context to OpenAI and formats social copy.
- `bot/poster.py`: publishes to Twitter/X via Tweepy and Telegram via Bot API.
- `bot/scheduler.py`: triggers `bot.run_cycle()` every day at the configured time.
- `scripts/run_bot.py`: command-line entrypoint supporting single-run or scheduled mode.

## Notes

- Keep credentials safe and never commit `.env`.
- Adjust `MAX_TRENDS_PER_RUN` and posting schedule in `.env`.
- Update `OPENAI_MODEL` for the latest supported chat model.
- This bot is designed to support future expansion with analytics, dashboard, and memory/history features.
