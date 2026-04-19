"""LLM-powered signal detection from news headlines."""
from __future__ import annotations

import json

import anthropic

from market_pulse.ai.prompts import SCANNER_SYSTEM, SCANNER_USER
from market_pulse.config import settings

_SIGNAL_TOOL: anthropic.types.ToolParam = {
    "name": "report_signals",
    "description": "Report detected trading signals from news",
    "input_schema": {
        "type": "object",
        "properties": {
            "signals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string"},
                        "signal": {"type": "string"},
                        "confidence": {"type": "number"},
                        "detail": {"type": "string"},
                    },
                    "required": ["ticker", "signal", "confidence", "detail"],
                },
            }
        },
        "required": ["signals"],
    },
}


async def scan_sector(sector: str, signal_filter: str, limit: int) -> list[dict[str, object]]:
    """Stub: returns empty list until a real sector ticker list is wired up."""
    return []


async def detect_signals(ticker: str, sector: str, articles: list[dict[str, object]]) -> list[dict[str, object]]:
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _detect_sync, ticker, sector, articles)


def _detect_sync(ticker: str, sector: str, articles: list[dict[str, object]]) -> list[dict[str, object]]:
    if not articles:
        return []
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    headlines = "\n".join(f"- {a.get('title', '')}" for a in articles[:20])
    user_msg = SCANNER_USER.format(ticker=ticker, sector=sector, headlines=headlines)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=SCANNER_SYSTEM,
        tools=[_SIGNAL_TOOL],
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": user_msg}],
    )
    tool_call = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_call is None:
        return []
    args: dict[str, object] = tool_call.input  # type: ignore[assignment]
    return args.get("signals", [])  # type: ignore[return-value]
