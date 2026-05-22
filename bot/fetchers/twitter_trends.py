import httpx
from typing import List

from ..config import settings
from ..models import TrendItem
from ..logger import logger

TWITTER_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"
DEFAULT_CRYPTO_HASHTAGS = ["#Bitcoin", "#Ethereum", "#Crypto", "#DeFi", "#Altcoins", "#BTC", "#ETH"]

async def fetch_twitter_trends() -> List[TrendItem]:
    trends: List[TrendItem] = []
    if not settings.twitter_bearer_token:
        logger.debug("Twitter bearer token missing; using default crypto hashtag seeds.")
        return [
            TrendItem(source="twitter", topic=tag, title=f"Trending hashtag {tag}", url=None)
            for tag in DEFAULT_CRYPTO_HASHTAGS
        ]

    headers = {"Authorization": f"Bearer {settings.twitter_bearer_token}"}
    query = " OR ".join([tag.strip("#") for tag in DEFAULT_CRYPTO_HASHTAGS]) + " lang:en -is:retweet"

    try:
        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            response = await client.get(TWITTER_SEARCH_URL, params={"query": query, "max_results": 20})
            response.raise_for_status()
            data = response.json()

        tweets = data.get("data", [])
        unique_topics = set()
        for tweet in tweets[:10]:
            text = tweet.get("text", "").strip()
            if not text or text in unique_topics:
                continue
            unique_topics.add(text)
            trends.append(
                TrendItem(source="twitter", topic=text, title=text, url=None, mentions=0, engagement=0)
            )
    except Exception as exc:
        logger.warning("Twitter trends fetch failed: %s", exc)
    return trends
