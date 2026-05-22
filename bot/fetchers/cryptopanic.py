import httpx
from typing import List

from ..config import settings
from ..models import TrendItem
from ..logger import logger

CRYPTOPANIC_API_URL = "https://cryptopanic.com/api/v1/posts/"

async def fetch_cryptopanic_trends() -> List[TrendItem]:
    trends: List[TrendItem] = []
    if not settings.cryptopanic_api_key:
        logger.debug("CryptoPanic API key missing, skipping CryptoPanic trends.")
        return trends

    params = {"auth_token": settings.cryptopanic_api_key, "kind": "news", "public": "true", "filter": "trending", "region": "us"}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(CRYPTOPANIC_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

        for item in data.get("results", [])[:6]:
            title = item.get("title")
            url = item.get("url")
            if title:
                trends.append(
                    TrendItem(
                        source="cryptopanic",
                        topic=title,
                        title=title,
                        url=url,
                        mentions=item.get("votes_sum", 0),
                        engagement=item.get("comments_count", 0),
                    )
                )
    except Exception as exc:
        logger.warning("CryptoPanic fetch failed: %s", exc)
    return trends
