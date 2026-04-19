import asyncio

import typer
from rich.console import Console

scan_app = typer.Typer(help="Scan a sector for trading signals")
console = Console()


@scan_app.callback(invoke_without_command=True)
def scan(
    sector: str = typer.Option(..., "--sector", "-s", help="Sector name"),
    signal: str = typer.Option("", "--signal", help="Signal filter e.g. earnings_beat"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
) -> None:
    """Scan a sector for stocks matching a signal pattern."""
    asyncio.run(_scan(sector, signal, limit))


async def _scan(sector: str, signal: str, limit: int) -> None:
    from market_pulse.ai.scanner import scan_sector

    console.print(f"[bold]Scanning sector: [cyan]{sector}[/cyan]  signal: [yellow]{signal or 'any'}[/yellow][/bold]")
    results = await scan_sector(sector, signal, limit)
    if not results:
        console.print("[yellow]No signals found.[/yellow]")
        return
    from rich.table import Table
    table = Table(title=f"Scan: {sector}")
    table.add_column("TICKER", style="cyan")
    table.add_column("SIGNAL")
    table.add_column("DETAIL")
    for r in results:
        table.add_row(r.get("ticker", ""), r.get("signal", ""), r.get("detail", ""))
    console.print(table)
