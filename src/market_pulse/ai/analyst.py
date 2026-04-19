"""Claude tool-use: structured investment analysis — never raw text parsing."""
from __future__ import annotations

from datetime import datetime, timezone

import anthropic

from market_pulse.ai.prompts import ANALYST_SYSTEM, ANALYST_USER
from market_pulse.config import settings
from market_pulse.models.market import AnalysisReport, MarketSnapshot

ANALYSIS_TOOLS: list[anthropic.types.ToolParam] = [
    {
        "name": "generate_analysis",
        "description": "Generate a structured investment analysis",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "2-3 sentence executive summary"},
                "bull_case": {"type": "string", "description": "Bull case thesis, newline-separated points"},
                "bear_case": {"type": "string", "description": "Bear case thesis, newline-separated points"},
                "key_risks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Top 3-5 risks",
                },
                "price_target_range": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "[low, high] 12-month price target",
                },
                "signals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key technical/fundamental signals",
                },
            },
            "required": ["summary", "bull_case", "bear_case", "key_risks", "signals"],
        },
    }
]


async def generate_report(snapshot: MarketSnapshot, depth: str = "standard") -> AnalysisReport:
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _generate_sync, snapshot, depth)


def _generate_sync(snapshot: MarketSnapshot, depth: str) -> AnalysisReport:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    f = snapshot.fundamentals
    p = snapshot.price
    s = snapshot.sentiment

    user_msg = ANALYST_USER.format(
        ticker=snapshot.ticker,
        close=p.close,
        volume=p.volume,
        vwap=p.vwap or "N/A",
        pe_ratio=f.pe_ratio or "N/A",
        ev_ebitda=f.ev_ebitda or "N/A",
        revenue_growth=f"{f.revenue_growth_yoy:.1%}" if f.revenue_growth_yoy else "N/A",
        gross_margin=f"{f.gross_margin:.1%}" if f.gross_margin else "N/A",
        debt_to_equity=f.debt_to_equity or "N/A",
        free_cash_flow=f.free_cash_flow or "N/A",
        eps_surprise=f.eps_surprise_pct or "N/A",
        technical_signals="\n".join(f"- {s}" for s in snapshot.technical_signals) or "None",
        sentiment_score=s.score,
        news_count=s.news_count,
        reddit_mentions=s.reddit_mentions,
        dominant_theme=s.dominant_theme or "None",
        anomalies="\n".join(f"- {a}" for a in snapshot.anomalies) or "None",
        depth=depth,
    )

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        system=ANALYST_SYSTEM,
        tools=ANALYSIS_TOOLS,
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": user_msg}],
    )

    tool_call = next(
        (block for block in response.content if block.type == "tool_use"),
        None,
    )
    if tool_call is None:
        raise RuntimeError("Claude did not call generate_analysis tool")

    args: dict[str, object] = tool_call.input  # type: ignore[assignment]
    pt = args.get("price_target_range")

    return AnalysisReport(
        ticker=snapshot.ticker,
        generated_at=datetime.now(timezone.utc),
        depth=depth,
        summary=str(args["summary"]),
        bull_case=str(args["bull_case"]),
        bear_case=str(args["bear_case"]),
        key_risks=[str(r) for r in args.get("key_risks", [])],  # type: ignore[union-attr]
        price_target_range=(float(pt[0]), float(pt[1])) if pt and len(pt) == 2 else None,  # type: ignore[index,arg-type]
        signals=[str(s) for s in args.get("signals", [])],  # type: ignore[union-attr]
        raw_data=snapshot,
    )
