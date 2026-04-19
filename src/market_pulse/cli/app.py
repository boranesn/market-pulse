import typer
from rich.console import Console

from market_pulse import __version__

app = typer.Typer(
    name="pulse",
    help="Async LLM-powered financial market intelligence CLI",
    no_args_is_help=True,
)
console = Console()


def _register_subcommands() -> None:
    from market_pulse.cli.alert import alert_app
    from market_pulse.cli.compare import compare_app
    from market_pulse.cli.report import report_app
    from market_pulse.cli.scan import scan_app
    from market_pulse.cli.watch import watch_app

    app.add_typer(watch_app, name="watch")
    app.add_typer(report_app, name="report")
    app.add_typer(scan_app, name="scan")
    app.add_typer(compare_app, name="compare")
    app.add_typer(alert_app, name="alert")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
) -> None:
    if version:
        console.print(f"market-pulse v{__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


_register_subcommands()
