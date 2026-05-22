from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class TrendItem:
    source: str
    topic: str
    title: str
    url: str | None
    score: float = 0.0
    sentiment: str = "neutral"
    mentions: int = 0
    engagement: int = 0
    extra: dict[str, Any] = None

    def normalized_topic(self) -> str:
        return self.topic.strip().lower()

@dataclass
class GeneratedPost:
    trend: TrendItem
    twitter_text: str
    telegram_text: str
    hashtags: list[str]
    image_prompt: str | None = None
    created_at: datetime = datetime.utcnow()
