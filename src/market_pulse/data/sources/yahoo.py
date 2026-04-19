from datetime import datetime, timezone
from decimal import Decimal

import yfinance as yf

from market_pulse.models.market import Fundamentals, PriceSnapshot


async def fetch_price(ticker: str) -> PriceSnapshot:
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_price_sync, ticker)


def _fetch_price_sync(ticker: str) -> PriceSnapshot:
    t = yf.Ticker(ticker)
    hist = t.history(period="1d", interval="1m")
    if hist.empty:
        raise ValueError(f"No price data for {ticker}")
    latest = hist.iloc[-1]
    info = t.fast_info
    return PriceSnapshot(
        ticker=ticker,
        timestamp=datetime.now(timezone.utc),
        open=Decimal(str(latest["Open"])),
        high=Decimal(str(latest["High"])),
        low=Decimal(str(latest["Low"])),
        close=Decimal(str(latest["Close"])),
        volume=int(latest["Volume"]),
        vwap=Decimal(str(info.get("three_month_average_volume", latest["Close"]))),
    )


async def fetch_fundamentals(ticker: str) -> Fundamentals:
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_fundamentals_sync, ticker)


def _fetch_fundamentals_sync(ticker: str) -> Fundamentals:
    t = yf.Ticker(ticker)
    info = t.info
    return Fundamentals(
        ticker=ticker,
        pe_ratio=info.get("trailingPE"),
        ev_ebitda=info.get("enterpriseToEbitda"),
        revenue_growth_yoy=info.get("revenueGrowth"),
        gross_margin=info.get("grossMargins"),
        debt_to_equity=info.get("debtToEquity"),
        free_cash_flow=info.get("freeCashflow"),
        eps_surprise_pct=None,
    )
