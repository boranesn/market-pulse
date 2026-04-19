import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

report_app = typer.Typer(help="Generate investment analysis report for a ticker")
console = Console()


@report_app.callback(invoke_without_command=True)
def report(
    ticker: str = typer.Argument(..., help="Ticker symbol"),
    depth: str = typer.Option("standard", "--depth", "-d", help="quick | standard | full"),
    format: str = typer.Option("terminal", "--format", "-f", help="terminal | markdown | pdf | json"),
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output file path")] = None,
) -> None:
    """Generate an analyst-grade investment report."""
    asyncio.run(_report(ticker, depth, format, output))


async def _report(ticker: str, depth: str, format: str, output: Path | None) -> None:
    from market_pulse.data.aggregator import fetch_all
    from market_pulse.ai.analyst import generate_report

    console.print(f"[bold]Fetching data for [cyan]{ticker}[/cyan]...[/bold]")
    snapshot = await fetch_all(ticker)

    console.print("[bold]Running AI analysis...[/bold]")
    report = await generate_report(snapshot, depth=depth)

    if format == "terminal":
        _render_terminal(report)
    elif format == "markdown":
        from market_pulse.export.markdown import render_markdown
        md = render_markdown(report)
        path = output or Path(f"{ticker}_report.md")
        path.write_text(md)
        console.print(f"[green]Saved to {path}[/green]")
    elif format == "pdf":
        from market_pulse.export.pdf import render_pdf
        path = output or Path(f"{ticker}_report.pdf")
        render_pdf(report, path)
        console.print(f"[green]Saved to {path}[/green]")
    elif format == "json":
        from market_pulse.export.json import render_json
        path = output or Path(f"{ticker}_report.json")
        path.write_text(render_json(report))
        console.print(f"[green]Saved to {path}[/green]")


def _render_terminal(report: object) -> None:
    from rich.panel import Panel
    from rich.text import Text
    from market_pulse.models.market import AnalysisReport

    r: AnalysisReport = report  # type: ignore[assignment]
    console.rule(f"[bold]{r.ticker} — {r.depth.capitalize()} Analysis Report  {r.generated_at.date()}[/bold]")
    console.print(f"\n[bold]Summary[/bold]\n{r.summary}\n")
    console.print(f"[bold green]Bull Case[/bold green]")
    for b in r.bull_case.split("\n"):
        console.print(f"  ▸ {b}")
    console.print(f"\n[bold red]Bear Case[/bold red]")
    for b in r.bear_case.split("\n"):
        console.print(f"  ▸ {b}")
    console.print(f"\n[bold yellow]Key Risks[/bold yellow]")
    for risk in r.key_risks:
        console.print(f"  ⚠ {risk}")
    if r.price_target_range:
        lo, hi = r.price_target_range
        console.print(f"\n[bold]Price Target[/bold]  ${lo:.0f} – ${hi:.0f}")
    console.rule()
