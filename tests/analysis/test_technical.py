import pytest
from market_pulse.analysis.technical import (
    compute_rsi,
    compute_sma,
    compute_ema,
    compute_bollinger,
    detect_volume_spike,
    compute_signals,
)


def _prices(n: int = 50) -> list[float]:
    import math
    return [100 + 10 * math.sin(i * 0.3) for i in range(n)]


def test_sma_length():
    prices = _prices(30)
    sma = compute_sma(prices, 20)
    assert len(sma) == 30
    assert sma[:19] == [None] * 19
    assert sma[19] is not None


def test_rsi_range():
    prices = _prices(50)
    rsi = compute_rsi(prices)
    for v in rsi:
        if v is not None:
            assert 0 <= v <= 100


def test_bollinger_upper_gt_lower():
    prices = _prices(50)
    upper, mid, lower = compute_bollinger(prices)
    for u, l in zip(upper, lower):
        if u is not None and l is not None:
            assert u >= l


def test_volume_spike_detection():
    # Normal volumes with one huge spike at the end
    volumes = [1_000_000] * 25 + [50_000_000]
    spikes = detect_volume_spike(volumes)
    assert spikes[-1] is True


def test_compute_signals_not_enough_data():
    assert compute_signals("AAPL", prices=[100.0] * 10) == []
