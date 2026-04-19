import asyncio
import smtplib
from email.message import EmailMessage

from market_pulse.config import settings


async def notify(ticker: str, message: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_sync, ticker, message)


def _send_sync(ticker: str, message: str) -> None:
    if not settings.smtp_user:
        return
    msg = EmailMessage()
    msg["Subject"] = f"market-pulse alert: {ticker}"
    msg["From"] = settings.smtp_user
    msg["To"] = settings.smtp_user
    msg.set_content(message)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(msg)
