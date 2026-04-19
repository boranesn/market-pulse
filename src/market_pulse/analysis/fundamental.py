"""Fundamental analysis: P/E context, EV/EBITDA, simple DCF, growth rates."""
from __future__ import annotations

from market_pulse.models.market import Fundamentals


def score_valuation(f: Fundamentals) -> dict[str, str]:
    """Return qualitative labels for key fundamental metrics."""
    result: dict[str, str] = {}
    if f.pe_ratio is not None:
        if f.pe_ratio < 15:
            result["pe"] = "undervalued"
        elif f.pe_ratio < 30:
            result["pe"] = "fair"
        else:
            result["pe"] = "expensive"

    if f.ev_ebitda is not None:
        if f.ev_ebitda < 10:
            result["ev_ebitda"] = "cheap"
        elif f.ev_ebitda < 20:
            result["ev_ebitda"] = "fair"
        else:
            result["ev_ebitda"] = "expensive"

    if f.gross_margin is not None:
        if f.gross_margin > 0.5:
            result["gross_margin"] = "high"
        elif f.gross_margin > 0.3:
            result["gross_margin"] = "moderate"
        else:
            result["gross_margin"] = "low"

    if f.debt_to_equity is not None:
        if f.debt_to_equity < 0.5:
            result["leverage"] = "low"
        elif f.debt_to_equity < 1.5:
            result["leverage"] = "moderate"
        else:
            result["leverage"] = "high"
    return result


def simple_dcf(
    free_cash_flow: float,
    growth_rate: float = 0.10,
    terminal_rate: float = 0.03,
    discount_rate: float = 0.10,
    years: int = 5,
    shares_outstanding: int = 1,
) -> float:
    """Very simplified DCF: sum discounted FCFs + terminal value."""
    pv = 0.0
    fcf = free_cash_flow
    for i in range(1, years + 1):
        fcf *= 1 + growth_rate
        pv += fcf / (1 + discount_rate) ** i
    terminal_value = fcf * (1 + terminal_rate) / (discount_rate - terminal_rate)
    pv += terminal_value / (1 + discount_rate) ** years
    return pv / shares_outstanding if shares_outstanding else pv


def fundamental_signals(f: Fundamentals) -> list[str]:
    signals: list[str] = []
    scores = score_valuation(f)
    if scores.get("pe") == "undervalued":
        signals.append("Low P/E — potential value")
    if scores.get("pe") == "expensive":
        signals.append("High P/E — growth priced in")
    if scores.get("gross_margin") == "high":
        signals.append("High gross margin — competitive moat")
    if scores.get("leverage") == "high":
        signals.append("High leverage — balance sheet risk")
    if f.revenue_growth_yoy and f.revenue_growth_yoy > 0.20:
        signals.append(f"Strong revenue growth ({f.revenue_growth_yoy:.0%} YoY)")
    if f.eps_surprise_pct and f.eps_surprise_pct > 5:
        signals.append(f"EPS beat by {f.eps_surprise_pct:.1f}%")
    return signals
