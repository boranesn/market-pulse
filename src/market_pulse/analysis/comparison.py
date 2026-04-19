"""Peer comparison and relative strength analysis."""
from __future__ import annotations

from market_pulse.models.market import Fundamentals, MarketSnapshot


def compare_fundamentals(snapshots: list[MarketSnapshot]) -> list[dict[str, object]]:
    """Return a ranked list of tickers by fundamental score."""
    results = []
    for snap in snapshots:
        score = _fundamental_score(snap.fundamentals)
        results.append({"ticker": snap.ticker, "score": score, "fundamentals": snap.fundamentals})
    results.sort(key=lambda x: x["score"], reverse=True)  # type: ignore[return-value]
    return results


def _fundamental_score(f: Fundamentals) -> float:
    score = 0.0
    if f.revenue_growth_yoy and f.revenue_growth_yoy > 0:
        score += min(f.revenue_growth_yoy * 100, 30)
    if f.gross_margin and f.gross_margin > 0:
        score += f.gross_margin * 20
    if f.pe_ratio and 0 < f.pe_ratio < 50:
        score += (50 - f.pe_ratio) / 50 * 20
    if f.debt_to_equity is not None and f.debt_to_equity < 2:
        score += (2 - f.debt_to_equity) * 5
    if f.eps_surprise_pct and f.eps_surprise_pct > 0:
        score += min(f.eps_surprise_pct, 10)
    return round(score, 2)


def relative_strength(prices_a: list[float], prices_b: list[float]) -> float:
    """RS ratio: last price change of A relative to B over same period."""
    if len(prices_a) < 2 or len(prices_b) < 2:
        return 1.0
    change_a = (prices_a[-1] - prices_a[0]) / prices_a[0]
    change_b = (prices_b[-1] - prices_b[0]) / prices_b[0]
    if change_b == 0:
        return 1.0
    return round((1 + change_a) / (1 + change_b), 4)
