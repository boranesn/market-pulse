from __future__ import annotations

import aiohttp

from market_pulse.config import settings

_BASE = "https://newsapi.org/v2/everything"


async def fetch_articles(ticker: str, page_size: int = 20) -> list[dict[str, object]]:
    """Fetch recent news articles mentioning the ticker."""
    params = {
        "q": ticker,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "language": "en",
        "apiKey": settings.news_api_key,
    }
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.request_timeout)) as session:
        async with session.get(_BASE, params=params) as resp:
            resp.raise_for_status()
            data: dict[str, object] = await resp.json()
            articles: list[dict[str, object]] = data.get("articles", [])  # type: ignore[assignment]
            return articles
