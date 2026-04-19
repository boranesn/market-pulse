"""Pure Polars technical analysis: SMA, EMA, RSI, MACD, Bollinger, volume spike."""
from __future__ import annotations

import polars as pl


def compute_sma(prices: list[float], period: int) -> list[float | None]:
    s = pl.Series("close", prices)
    result = s.rolling_mean(window_size=period)
    return result.to_list()


def compute_ema(prices: list[float], period: int) -> list[float | None]:
    s = pl.Series("close", prices)
    result = s.ewm_mean(span=period, adjust=False)
    return result.to_list()


def compute_rsi(prices: list[float], period: int = 14) -> list[float | None]:
    s = pl.Series("close", prices)
    delta = s.diff()
    gain = delta.map_elements(lambda x: x if x > 0 else 0.0, return_dtype=pl.Float64)
    loss = delta.map_elements(lambda x: -x if x < 0 else 0.0, return_dtype=pl.Float64)
    avg_gain = gain.rolling_mean(window_size=period)
    avg_loss = loss.rolling_mean(window_size=period)
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.to_list()


def compute_macd(
    prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    s = pl.Series("close", prices)
    ema_fast = s.ewm_mean(span=fast, adjust=False)
    ema_slow = s.ewm_mean(span=slow, adjust=False)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm_mean(span=signal, adjust=False)
    histogram = macd_line - signal_line
    return macd_line.to_list(), signal_line.to_list(), histogram.to_list()


def compute_bollinger(
    prices: list[float], period: int = 20, std_dev: float = 2.0
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    s = pl.Series("close", prices)
    middle = s.rolling_mean(window_size=period)
    std = s.rolling_std(window_size=period)
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    return upper.to_list(), middle.to_list(), lower.to_list()


def detect_volume_spike(volumes: list[int], threshold: float = 2.0) -> list[bool]:
    s = pl.Series("volume", volumes, dtype=pl.Float64)
    mean = s.rolling_mean(window_size=20)
    spike = s > (mean * threshold)
    return spike.to_list()


def compute_signals(ticker: str, prices: list[float] | None = None, volumes: list[int] | None = None) -> list[str]:
    """Generate human-readable signals from price/volume series."""
    if not prices or len(prices) < 26:
        return []
    signals: list[str] = []
    rsi = compute_rsi(prices)
    last_rsi = next((v for v in reversed(rsi) if v is not None), None)
    if last_rsi is not None:
        if last_rsi < 30:
            signals.append("RSI oversold")
        elif last_rsi > 70:
            signals.append("RSI overbought")

    sma200 = compute_sma(prices, 200) if len(prices) >= 200 else [None]
    sma50 = compute_sma(prices, 50) if len(prices) >= 50 else [None]
    last_price = prices[-1]
    last_sma200 = next((v for v in reversed(sma200) if v is not None), None)
    last_sma50 = next((v for v in reversed(sma50) if v is not None), None)

    if last_sma200 and last_price > last_sma200:
        signals.append("Above 200-day MA")
    if last_sma50 and last_sma200 and last_sma50 < last_sma200:
        signals.append("Death cross")
    elif last_sma50 and last_sma200 and last_sma50 > last_sma200:
        signals.append("Golden cross")

    if volumes:
        spikes = detect_volume_spike(volumes)
        if spikes and spikes[-1]:
            signals.append("Volume spike")
    return signals
