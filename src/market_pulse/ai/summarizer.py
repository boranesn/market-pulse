"""Summarize SEC filings and earnings transcripts via Claude."""
from __future__ import annotations

import anthropic

from market_pulse.ai.prompts import SUMMARIZER_SYSTEM, SUMMARIZER_USER
from market_pulse.config import settings


async def summarize_filing(ticker: str, doc_type: str, content: str) -> str:
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _summarize_sync, ticker, doc_type, content)


def _summarize_sync(ticker: str, doc_type: str, content: str) -> str:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    user_msg = SUMMARIZER_USER.format(doc_type=doc_type, ticker=ticker, content=content[:8000])
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=SUMMARIZER_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text  # type: ignore[union-attr]
