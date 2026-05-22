import httpx
from bs4 import BeautifulSoup

from ..models import TrendItem
from ..logger import logger

CMC_TREND_URL = "https://coinmarketcap.com/trending-cryptocurrencies/"

async def fetch_coinmarketcap_trends() -> list[TrendItem]:
    trends: list[TrendItem] = []
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(CMC_TREND_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

        rows = soup.select("table tr")[:8]
        for row in rows:
            name_tag = row.select_one("td:nth-of-type(3) a")
            if not name_tag:
                continue
            title = name_tag.get_text(strip=True)
            url = f"https://coinmarketcap.com{name_tag['href']}" if name_tag.has_attr("href") else CMC_TREND_URL
            trends.append(
                TrendItem(
                    source="coinmarketcap",
                    topic=title,
                    title=f"Trending crypto: {title}",
                    url=url,
                    mentions=0,
                    engagement=0,
                )
            )
    except Exception as exc:
        logger.warning("CoinMarketCap fetch failed: %s", exc)
    return trends
