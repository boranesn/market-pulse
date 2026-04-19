import asyncio

import typer
from rich.console import Console

watch_app = typer.Typer(help="Live watch tickers in real-time dashboard")
console = Console()


@watch_app.callback(invoke_without_command=True)
def watch(
    tickers: list[str] = typer.Argument(..., help="Ticker symbols to watch"),
    interval: int = typer.Option(60, "--interval", "-i", help="Refresh interval in seconds"),
) -> None:
    """Live dashboard watching one or more tickers."""
    asyncio.run(_watch(tickers, interval))


async def _watch(tickers: list[str], interval: int) -> None:
    from rich.live import Live
    from rich.table import Table

    import time

    console.print(f"[bold green]Watching {', '.join(tickers)} every {interval}s[/bold green]")
    console.print("Press Ctrl+C to quit")

    try:
        while True:
            table = Table(title="market-pulse · Live Watch")
            table.add_column("TICKER", style="cyan")
            table.add_column("PRICE")
            table.add_column("CHG")
            table.add_column("SENT")
            table.add_column("SIGNAL")

            for ticker in tickers:
                try:
                    from market_pulse.data.aggregator import fetch_all
                    from market_pulse.analysis.technical import compute_signals

                    snapshot = await fetch_all(ticker)
                    signals = compute_signals(ticker)
                    signal_str = signals[0] if signals else "-"
                    table.add_row(
                        ticker,
                        f"{snapshot.price.close:.2f}",
                        "-",
                        f"{snapshot.sentiment.score:.2f}",
                        signal_str,
                    )
                except Exception as exc:
                    table.add_row(ticker, "[red]ERR[/red]", "-", "-", str(exc)[:20])

            console.clear()
            console.print(table)
            console.print(f"  Refreshing in {interval}s  ·  Press Ctrl+C to quit")
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped.[/yellow]")
