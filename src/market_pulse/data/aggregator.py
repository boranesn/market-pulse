import asyncio
from datetime import datetime, timezone

from market_pulse.data.sources import newsapi, reddit, sec, yahoo
from market_pulse.data.normalizer import normalize
from market_pulse.models.market import MarketSnapshot


async def fetch_all(ticker: str) -> MarketSnapshot:
    """Fan-out across all data sources concurrently; total latency = slowest source."""
    ticker = ticker.upper()
    async with asyncio.TaskGroup() as tg:
        price_task = tg.create_task(yahoo.fetch_price(ticker))
        fund_task = tg.create_task(yahoo.fetch_fundamentals(ticker))
        news_task = tg.create_task(_safe(newsapi.fetch_articles(ticker), []))
        sec_task = tg.create_task(_safe(sec.fetch_latest_filing(ticker), {}))
        reddit_task = tg.create_task(_safe(reddit.fetch_mentions(ticker), []))

    return normalize(
        ticker=ticker,
        fetched_at=datetime.now(timezone.utc),
        price=price_task.result(),
        fundamentals=fund_task.result(),
        news_articles=news_task.result(),
        sec_filing=sec_task.result(),
        reddit_posts=reddit_task.result(),
    )


async def _safe(coro: object, default: object) -> object:
    """Swallow errors from optional sources so one failure doesn't abort the whole fetch."""
    import asyncio as _asyncio
    try:
        return await coro  # type: ignore[misc]
    except Exception:
        return default
