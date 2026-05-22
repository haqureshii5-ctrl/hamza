import asyncio
from typing import list
from bs4 import BeautifulSoup
import httpx

from ..models import TrendItem
from ..logger import logger

BINANCE_SQUARE_URL = "https://www.binance.com/en/square"

async def fetch_binance_square_trends() -> list[TrendItem]:
    trends: list[TrendItem] = []
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(BINANCE_SQUARE_URL)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "lxml")
        cards = soup.select(".css-1y5w9aw .css-1d5czl0, .css-1azzwi0")[:6]
        for card in cards:
            title = card.get_text(separator=" ", strip=True)
            if not title:
                continue
            trends.append(
                TrendItem(
                    source="binance_square",
                    topic=title,
                    title=title,
                    url=BINANCE_SQUARE_URL,
                    mentions=0,
                    engagement=0,
                )
            )
    except Exception as exc:
        logger.warning("Binance Square fetch failed: %s", exc)
    return trends
