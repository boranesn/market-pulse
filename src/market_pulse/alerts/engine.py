"""Alert evaluation loop using APScheduler."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from market_pulse.alerts.conditions import evaluate
from market_pulse.data.aggregator import fetch_all
from market_pulse.storage.db import get_connection


async def start_engine(poll_interval: int = 60) -> None:
    """Poll all active alerts on a fixed interval until cancelled."""
    while True:
        try:
            await _evaluate_all_alerts()
        except Exception as exc:
            print(f"[alert engine] error: {exc}")
        await asyncio.sleep(poll_interval)


async def _evaluate_all_alerts() -> None:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, ticker, condition_expr, notify_via FROM alerts"
    ).fetchall()

    for row in rows:
        alert_id, ticker, condition_expr, notify_via_raw = row
        try:
            snapshot = await fetch_all(ticker)
            triggered = evaluate(condition_expr, snapshot)
            if triggered:
                await _fire_alert(str(alert_id), ticker, condition_expr, notify_via_raw)
                conn.execute(
                    "UPDATE alerts SET last_triggered = ?, trigger_count = trigger_count + 1 WHERE id = ?",
                    [datetime.now(timezone.utc), alert_id],
                )
        except Exception as exc:
            print(f"[alert] {ticker} / {condition_expr}: {exc}")


async def _fire_alert(alert_id: str, ticker: str, condition: str, notify_via_raw: object) -> None:
    from market_pulse.alerts.notifiers.terminal import notify as terminal_notify

    message = f"ALERT [{ticker}]: {condition} triggered"
    await terminal_notify(ticker, message)

    notify_channels: list[str] = []
    try:
        import json
        notify_channels = json.loads(str(notify_via_raw))
    except Exception:
        pass

    if "slack" in notify_channels:
        from market_pulse.alerts.notifiers.slack import notify as slack_notify
        await slack_notify(ticker, message)
    if "email" in notify_channels:
        from market_pulse.alerts.notifiers.email import notify as email_notify
        await email_notify(ticker, message)
