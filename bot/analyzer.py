import re
from statistics import mean
from typing import Iterable

from .models import TrendItem
from .logger import logger
from .utils import normalize_topic

POSITIVE_SIGNAL = ["bull", "moon", "long", "buy", "breakout", "rally", "accumulate", "green", "surge"]
NEGATIVE_SIGNAL = ["dump", "sell", "bear", "drop", "capitulate", "weak", "red", "fud", "rejection"]


def analyze_sentiment(text: str) -> str:
    text_lower = text.lower()
    positive = sum(1 for token in POSITIVE_SIGNAL if token in text_lower)
    negative = sum(1 for token in NEGATIVE_SIGNAL if token in text_lower)
    if positive > negative:
        return "bullish"
    if negative > positive:
        return "bearish"
    return "neutral"


def compute_score(trend: TrendItem) -> float:
    weights = [
        min(trend.mentions / 100, 1.0),
        min(trend.engagement / 200, 1.0),
    ]
    sentiment_bonus = 0.15 if trend.sentiment == "bullish" else -0.1 if trend.sentiment == "bearish" else 0.0
    text_length_bonus = 0.05 if len(trend.title) < 120 else 0.0
    score = mean(weights) + sentiment_bonus + text_length_bonus
    normalized = max(0.0, min(score, 1.0))
    logger.debug("Trend score %s => %.3f", trend.topic, normalized)
    return normalized


def dedupe_trends(trends: Iterable[TrendItem]) -> list[TrendItem]:
    seen: dict[str, TrendItem] = {}
    for item in trends:
        key = normalize_topic(item.topic)
        if key not in seen or item.engagement > seen[key].engagement:
            seen[key] = item
    return list(seen.values())


def analyze_trends(trend_items: Iterable[TrendItem]) -> list[TrendItem]:
    scored = []
    for item in trend_items:
        item.sentiment = analyze_sentiment(item.title)
        item.score = compute_score(item)
        scored.append(item)
    return sorted(scored, key=lambda value: value.score, reverse=True)
