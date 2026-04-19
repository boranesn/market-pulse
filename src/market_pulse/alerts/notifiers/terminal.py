from rich.console import Console

_console = Console()


async def notify(ticker: str, message: str) -> None:
    _console.print(f"[bold yellow]⚠ ALERT[/bold yellow] [[cyan]{ticker}[/cyan]] {message}")
