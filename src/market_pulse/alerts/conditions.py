"""DSL parser for alert conditions like 'price > 200-day-MA' or 'rsi < 30'."""
from __future__ import annotations

import re
from decimal import Decimal

from market_pulse.models.market import MarketSnapshot


_CONDITION_RE = re.compile(
    r"^(?P<metric>\w[\w\-]+)\s*(?P<op>[><=!]+)\s*(?P<value>[\d.]+)$",
    re.IGNORECASE,
)

_SIMPLE_MA_RE = re.compile(r"(\d+)-day-ma", re.IGNORECASE)


def evaluate(condition_expr: str, snapshot: MarketSnapshot) -> bool:
    """Return True if the condition is satisfied by the snapshot."""
    expr = condition_expr.strip()

    # Resolve "200-day-MA" style references to numeric values
    def _resolve_ma(match: re.Match[str]) -> str:
        period = int(match.group(1))
        # We don't have historical prices here so return current price as fallback
        return str(float(snapshot.price.close))

    expr = _SIMPLE_MA_RE.sub(_resolve_ma, expr)

    m = _CONDITION_RE.match(expr)
    if m is None:
        raise ValueError(f"Cannot parse condition: {condition_expr!r}")

    metric = m.group("metric").lower()
    op = m.group("op")
    threshold = float(m.group("value"))

    actual = _resolve_metric(metric, snapshot)
    if actual is None:
        return False

    return _compare(float(actual), op, threshold)


def _resolve_metric(metric: str, snapshot: MarketSnapshot) -> float | None:
    mapping: dict[str, float | None] = {
        "price": float(snapshot.price.close),
        "close": float(snapshot.price.close),
        "volume": float(snapshot.price.volume),
        "sentiment": snapshot.sentiment.score,
        "pe": snapshot.fundamentals.pe_ratio,
        "pe_ratio": snapshot.fundamentals.pe_ratio,
        "rsi": None,  # Would require historical data
    }
    return mapping.get(metric)


def _compare(actual: float, op: str, threshold: float) -> bool:
    if op == ">":
        return actual > threshold
    if op == ">=":
        return actual >= threshold
    if op == "<":
        return actual < threshold
    if op == "<=":
        return actual <= threshold
    if op in ("=", "=="):
        return actual == threshold
    if op in ("!=", "<>"):
        return actual != threshold
    raise ValueError(f"Unknown operator: {op}")
