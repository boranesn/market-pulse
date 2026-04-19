import asyncio
import uuid
from datetime import datetime, timezone

import typer
from rich.console import Console
from rich.table import Table

alert_app = typer.Typer(help="Manage price/condition alerts")
console = Console()


@alert_app.command("add")
def alert_add(
    ticker: str = typer.Argument(..., help="Ticker symbol"),
    condition: str = typer.Option(..., "--condition", "-c", help='Condition e.g. "price > 200-day-MA"'),
    notify: list[str] = typer.Option(["terminal"], "--notify", "-n", help="Notification channel"),
) -> None:
    """Add a new alert."""
    from market_pulse.storage.db import get_connection
    conn = get_connection()
    alert_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO alerts (id, ticker, condition_expr, notify_via, created_at) VALUES (?, ?, ?, ?, ?)",
        [alert_id, ticker, condition, str(notify), datetime.now(timezone.utc)],
    )
    console.print(f"[green]Alert added:[/green] {ticker} — {condition}  (id: {alert_id[:8]}...)")


@alert_app.command("list")
def alert_list() -> None:
    """List all alerts."""
    from market_pulse.storage.db import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT id, ticker, condition_expr, trigger_count FROM alerts").fetchall()
    table = Table(title="Alerts")
    table.add_column("ID")
    table.add_column("TICKER", style="cyan")
    table.add_column("CONDITION")
    table.add_column("TRIGGERS")
    for row in rows:
        table.add_row(str(row[0])[:8] + "...", row[1], row[2], str(row[3]))
    console.print(table)


@alert_app.command("delete")
def alert_delete(
    alert_id: str = typer.Argument(..., help="Alert ID prefix"),
) -> None:
    """Delete an alert by ID prefix."""
    from market_pulse.storage.db import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM alerts WHERE id::VARCHAR LIKE ?", [f"{alert_id}%"])
    console.print(f"[yellow]Deleted alert(s) matching[/yellow] {alert_id}")


@alert_app.command("run")
def alert_run() -> None:
    """Start the alert polling engine."""
    asyncio.run(_run_engine())


async def _run_engine() -> None:
    from market_pulse.alerts.engine import start_engine
    console.print("[bold green]Alert engine started. Press Ctrl+C to stop.[/bold green]")
    await start_engine()
