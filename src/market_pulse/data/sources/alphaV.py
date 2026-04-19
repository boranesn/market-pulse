from __future__ import annotations

import aiohttp

from market_pulse.config import settings

_BASE = "https://www.alphavantage.co/query"


async def fetch_technicals(ticker: str) -> dict[str, object]:
    """Fetch RSI and SMA from Alpha Vantage."""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.request_timeout)) as session:
        rsi = await _get(session, {"function": "RSI", "symbol": ticker, "interval": "daily",
                                   "time_period": 14, "series_type": "close"})
        sma20 = await _get(session, {"function": "SMA", "symbol": ticker, "interval": "daily",
                                     "time_period": 20, "series_type": "close"})
        return {"rsi": rsi, "sma20": sma20}


async def fetch_earnings(ticker: str) -> dict[str, object]:
    """Fetch latest earnings surprise."""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=settings.request_timeout)) as session:
        return await _get(session, {"function": "EARNINGS", "symbol": ticker})


async def _get(session: aiohttp.ClientSession, params: dict[str, object]) -> dict[str, object]:
    params["apikey"] = settings.alpha_vantage_api_key
    async with session.get(_BASE, params=params) as resp:  # type: ignore[arg-type]
        resp.raise_for_status()
        return await resp.json()  # type: ignore[return-value]
