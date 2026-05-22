import httpx
from typing import List

from ..config import settings
from ..models import TrendItem
from ..logger import logger

REDDIT_URL = "https://www.reddit.com/r/CryptoCurrency/top/.json"

async def fetch_reddit_trends() -> List[TrendItem]:
    trends: List[TrendItem] = []
    params = {"limit": 8, "t": "day"}
    headers = {"User-Agent": settings.reddit_user_agent}

    try:
        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            response = await client.get(REDDIT_URL, params=params)
            response.raise_for_status()
            payload = response.json()

        for post in payload.get("data", {}).get("children", [])[:8]:
            data = post.get("data", {})
            title = data.get("title")
            url = data.get("url")
            if title:
                trends.append(
                    TrendItem(
                        source="reddit",
                        topic=title,
                        title=title,
                        url=url,
                        mentions=data.get("num_comments", 0),
                        engagement=data.get("score", 0),
                    )
                )
    except Exception as exc:
        logger.warning("Reddit trend fetch failed: %s", exc)
    return trends
