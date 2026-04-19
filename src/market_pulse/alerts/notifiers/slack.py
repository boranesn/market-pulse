import aiohttp

from market_pulse.config import settings


async def notify(ticker: str, message: str) -> None:
    if not settings.slack_webhook_url:
        return
    payload = {"text": f":chart_with_upwards_trend: *{ticker}* — {message}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(settings.slack_webhook_url, json=payload) as resp:
            resp.raise_for_status()
