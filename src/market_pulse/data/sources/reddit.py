from __future__ import annotations

import asyncio

from market_pulse.config import settings


async def fetch_mentions(ticker: str, limit: int = 50) -> list[dict[str, object]]:
    """Fetch recent Reddit posts mentioning the ticker."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_sync, ticker, limit)


def _fetch_sync(ticker: str, limit: int) -> list[dict[str, object]]:
    import praw

    reddit = praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
        read_only=True,
    )
    results: list[dict[str, object]] = []
    for sub in ("wallstreetbets", "investing", "stocks"):
        for post in reddit.subreddit(sub).search(ticker, limit=limit // 3, sort="new"):
            results.append({
                "title": post.title,
                "score": post.score,
                "subreddit": sub,
                "created_utc": post.created_utc,
                "url": post.url,
            })
    return results
