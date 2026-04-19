from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from market_pulse.models.market import Fundamentals, PriceSnapshot, SentimentScore


@pytest.fixture
def mock_price():
    return PriceSnapshot(
        ticker="AAPL",
        timestamp=datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc),
        open=Decimal("188.00"),
        high=Decimal("191.05"),
        low=Decimal("187.50"),
        close=Decimal("189.42"),
        volume=52_000_000,
    )


@pytest.fixture
def mock_fundamentals():
    return Fundamentals(ticker="AAPL", pe_ratio=28.5)


@pytest.mark.asyncio
async def test_fetch_all_returns_snapshot(mock_price, mock_fundamentals):
    with (
        patch("market_pulse.data.sources.yahoo.fetch_price", new_callable=AsyncMock, return_value=mock_price),
        patch("market_pulse.data.sources.yahoo.fetch_fundamentals", new_callable=AsyncMock, return_value=mock_fundamentals),
        patch("market_pulse.data.sources.newsapi.fetch_articles", new_callable=AsyncMock, return_value=[]),
        patch("market_pulse.data.sources.sec.fetch_latest_filing", new_callable=AsyncMock, return_value={}),
        patch("market_pulse.data.sources.reddit.fetch_mentions", new_callable=AsyncMock, return_value=[]),
    ):
        from market_pulse.data.aggregator import fetch_all
        snapshot = await fetch_all("AAPL")
        assert snapshot.ticker == "AAPL"
        assert snapshot.price.close == Decimal("189.42")
        assert snapshot.fundamentals.pe_ratio == 28.5


@pytest.mark.asyncio
async def test_fetch_all_tolerates_source_failure(mock_price, mock_fundamentals):
    """Optional sources failing should not abort the whole fetch."""
    with (
        patch("market_pulse.data.sources.yahoo.fetch_price", new_callable=AsyncMock, return_value=mock_price),
        patch("market_pulse.data.sources.yahoo.fetch_fundamentals", new_callable=AsyncMock, return_value=mock_fundamentals),
        patch("market_pulse.data.sources.newsapi.fetch_articles", new_callable=AsyncMock, side_effect=Exception("API down")),
        patch("market_pulse.data.sources.sec.fetch_latest_filing", new_callable=AsyncMock, side_effect=Exception("timeout")),
        patch("market_pulse.data.sources.reddit.fetch_mentions", new_callable=AsyncMock, return_value=[]),
    ):
        from market_pulse.data.aggregator import fetch_all
        snapshot = await fetch_all("AAPL")
        assert snapshot.ticker == "AAPL"
        assert snapshot.sentiment.news_count == 0
