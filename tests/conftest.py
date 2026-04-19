from datetime import datetime, timezone
from decimal import Decimal

import pytest

from market_pulse.models.market import (
    Fundamentals,
    MarketSnapshot,
    PriceSnapshot,
    SentimentScore,
)
from market_pulse.storage.db import get_memory_connection


@pytest.fixture
def db():
    """In-memory DuckDB connection with schema applied."""
    conn = get_memory_connection()
    yield conn
    conn.close()


@pytest.fixture
def sample_price() -> PriceSnapshot:
    return PriceSnapshot(
        ticker="AAPL",
        timestamp=datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc),
        open=Decimal("188.00"),
        high=Decimal("191.05"),
        low=Decimal("187.50"),
        close=Decimal("189.42"),
        volume=52_000_000,
        vwap=Decimal("189.10"),
    )


@pytest.fixture
def sample_fundamentals() -> Fundamentals:
    return Fundamentals(
        ticker="AAPL",
        pe_ratio=28.5,
        ev_ebitda=18.2,
        revenue_growth_yoy=0.08,
        gross_margin=0.44,
        debt_to_equity=1.73,
        free_cash_flow=99_584_000_000,
        eps_surprise_pct=3.2,
    )


@pytest.fixture
def sample_sentiment() -> SentimentScore:
    return SentimentScore(
        ticker="AAPL",
        score=0.62,
        confidence=0.78,
        news_count=15,
        reddit_mentions=340,
        dominant_theme="iPhone upgrade cycle",
    )


@pytest.fixture
def sample_snapshot(
    sample_price: PriceSnapshot,
    sample_fundamentals: Fundamentals,
    sample_sentiment: SentimentScore,
) -> MarketSnapshot:
    return MarketSnapshot(
        ticker="AAPL",
        fetched_at=datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc),
        price=sample_price,
        fundamentals=sample_fundamentals,
        sentiment=sample_sentiment,
        technical_signals=["RSI oversold", "Above 200-day MA"],
        anomalies=[],
    )
