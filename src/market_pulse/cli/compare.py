import asyncio

import typer
from rich.console import Console

compare_app = typer.Typer(help="Compare tickers side-by-side")
console = Console()


@compare_app.callback(invoke_without_command=True)
def compare(
    tickers: list[str] = typer.Argument(..., help="Ticker symbols to compare"),
    metric: str = typer.Option("revenue_growth", "--metric", "-m", help="Metric to compare"),
    years: int = typer.Option(3, "--years", "-y", help="Years of history"),
) -> None:
    """Side-by-side peer comparison table."""
    asyncio.run(_compare(tickers, metric, years))


async def _compare(tickers: list[str], metric: str, years: int) -> None:
    import asyncio as _asyncio
    from market_pulse.data.aggregator import fetch_all

    console.print(f"[bold]Comparing {', '.join(tickers)} on [cyan]{metric}[/cyan][/bold]")
    snapshots = await _asyncio.gather(*[fetch_all(t) for t in tickers])

    from rich.table import Table
    table = Table(title=f"Comparison: {metric}")
    table.add_column("METRIC")
    for t in tickers:
        table.add_column(t, style="cyan")

    metrics_map = {
        "pe_ratio": "P/E Ratio",
        "ev_ebitda": "EV/EBITDA",
        "revenue_growth": "Revenue Growth YoY",
        "gross_margin": "Gross Margin",
        "debt_to_equity": "Debt/Equity",
    }
    label = metrics_map.get(metric, metric)
    values = []
    for snap in snapshots:
        val = getattr(snap.fundamentals, metric, None)
        values.append(f"{val:.2f}" if isinstance(val, float) else str(val or "-"))
    table.add_row(label, *values)
    console.print(table)
