import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Any

from .config import settings
from .logger import logger

DB_PATH = Path(settings.database_url.replace("sqlite://", ""))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS posted_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    score REAL,
    sentiment TEXT,
    hashtags TEXT,
    twitter_text TEXT,
    telegram_text TEXT,
    extra_json TEXT,
    posted_at TEXT NOT NULL,
    UNIQUE(source, topic)
);
"""

class Database:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self._connection = sqlite3.connect(str(path), check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._connection:
            self._connection.execute(CREATE_TABLE_SQL)
        logger.debug("Database schema ensured.")

    def has_topic(self, source: str, topic: str) -> bool:
        normalized = topic.strip().lower()
        query = "SELECT 1 FROM posted_trends WHERE source = ? AND lower(topic) = ? LIMIT 1"
        row = self._connection.execute(query, (source, normalized)).fetchone()
        return row is not None

    def save_post(self, source: str, topic: str, title: str, url: str | None, score: float, sentiment: str, hashtags: list[str], twitter_text: str, telegram_text: str, extra: dict[str, Any] | None = None) -> None:
        payload = json.dumps(extra or {}, ensure_ascii=False)
        posted_at = datetime.utcnow().isoformat()
        with self._connection:
            self._connection.execute(
                """
                INSERT OR IGNORE INTO posted_trends (source, topic, title, url, score, sentiment, hashtags, twitter_text, telegram_text, extra_json, posted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source,
                    topic,
                    title,
                    url,
                    score,
                    sentiment,
                    ",".join(hashtags),
                    twitter_text,
                    telegram_text,
                    payload,
                    posted_at,
                ),
            )
        logger.info("Saved post history: %s / %s", source, topic)

    def close(self) -> None:
        self._connection.close()
