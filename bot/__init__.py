import asyncio
from typing import Iterable

from .config import settings
from .fetchers import (
    fetch_binance_square_trends,
    fetch_coinmarketcap_trends,
    fetch_cryptopanic_trends,
    fetch_reddit_trends,
    fetch_twitter_trends,
)
from .analyzer import analyze_trends, dedupe_trends
from .generator import OpenAIGenerator
from .poster import SocialPoster
from .storage import Database
from .logger import logger
from .models import TrendItem, GeneratedPost


class CryptoTrendBot:
    def __init__(self) -> None:
        self.db = Database()
        self.generator = OpenAIGenerator()
        self.poster = SocialPoster()
        self.sources = [
            fetch_binance_square_trends,
            fetch_coinmarketcap_trends,
            fetch_cryptopanic_trends,
            fetch_reddit_trends,
            fetch_twitter_trends,
        ]

    async def _retry(self, coro, retries: int = 2, delay: float = 5.0):
        for attempt in range(1, retries + 2):
            try:
                return await coro()
            except Exception as exc:
                logger.warning("Attempt %s failed: %s", attempt, exc)
                if attempt >= retries + 1:
                    raise
                await asyncio.sleep(delay)

    async def collect_trends(self) -> list[TrendItem]:
        tasks = [source() for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        items: list[TrendItem] = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Source fetch error: %s", result)
                continue
            items.extend(result)
        logger.info("Collected %s raw trends", len(items))
        return items

    async def pick_trends(self) -> list[TrendItem]:
        trends = await self.collect_trends()
        trends = dedupe_trends(trends)
        trends = analyze_trends(trends)
        chosen: list[TrendItem] = []
        for trend in trends:
            if len(chosen) >= settings.max_trends_per_run:
                break
            if self.db.has_topic(trend.source, trend.normalized_topic()):
                logger.debug("Skipping duplicate topic from %s: %s", trend.source, trend.topic)
                continue
            chosen.append(trend)
        logger.info("Selected %s trends for posting", len(chosen))
        return chosen

    async def publish_trend(self, trend: TrendItem) -> None:
        try:
            post = await self._retry(lambda: self.generator.generate_post(trend))
            tweet_id = self.poster.post_twitter(post)
            telegram_id = await self._retry(lambda: self.poster.post_telegram(post))
            self.db.save_post(
                source=trend.source,
                topic=trend.normalized_topic(),
                title=trend.title,
                url=trend.url,
                score=trend.score,
                sentiment=trend.sentiment,
                hashtags=post.hashtags,
                twitter_text=post.twitter_text,
                telegram_text=post.telegram_text,
                extra={"tweet_id": tweet_id, "telegram_id": telegram_id},
            )
        except Exception as exc:
            logger.error("Failed to publish trend %s: %s", trend.topic, exc)

    async def run_cycle(self) -> None:
        logger.info("Starting trend cycle")
        trends = await self.pick_trends()
        if not trends:
            logger.info("No new trends available to post.")
            return
        for trend in trends:
            await self.publish_trend(trend)
        logger.info("Completed trend posting cycle")

    def close(self) -> None:
        self.db.close()


bot = CryptoTrendBot()
