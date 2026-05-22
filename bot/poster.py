import json
from typing import Optional
import tweepy
import httpx

from .config import settings
from .logger import logger
from .models import GeneratedPost

class SocialPoster:
    def __init__(self) -> None:
        self.twitter_client = None
        if settings.twitter_enabled and settings.twitter_api_key and settings.twitter_api_secret and settings.twitter_access_token and settings.twitter_access_secret:
            self.twitter_client = tweepy.Client(
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_secret,
            )

    def post_twitter(self, post: GeneratedPost) -> Optional[str]:
        if not settings.twitter_enabled or not self.twitter_client:
            logger.info("Twitter posting disabled or credentials missing.")
            return None

        try:
            response = self.twitter_client.create_tweet(text=post.twitter_text)
            tweet_id = str(response.data.get("id")) if response and response.data else None
            logger.info("Posted to Twitter/X: %s", tweet_id)
            return tweet_id
        except Exception as exc:
            logger.error("Twitter post failed: %s", exc)
            return None

    async def post_telegram(self, post: GeneratedPost) -> Optional[str]:
        if not settings.telegram_enabled or not settings.telegram_bot_token or not settings.telegram_chat_id:
            logger.info("Telegram posting disabled or credentials missing.")
            return None

        url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": settings.telegram_chat_id,
            "text": post.telegram_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
            message_id = str(result.get("result", {}).get("message_id"))
            logger.info("Posted to Telegram: %s", message_id)
            return message_id
        except Exception as exc:
            logger.error("Telegram post failed: %s", exc)
            return None
