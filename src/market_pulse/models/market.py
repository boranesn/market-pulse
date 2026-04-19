from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PriceSnapshot(BaseModel):
    ticker: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    vwap: Decimal | None = None


class Fundamentals(BaseModel):
    ticker: str
    pe_ratio: float | None = None
    ev_ebitda: float | None = None
    revenue_growth_yoy: float | None = None
    gross_margin: float | None = None
    debt_to_equity: float | None = None
    free_cash_flow: int | None = None
    eps_surprise_pct: float | None = None


class SentimentScore(BaseModel):
    ticker: str
    score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    news_count: int = 0
    reddit_mentions: int = 0
    dominant_theme: str = ""


class MarketSnapshot(BaseModel):
    ticker: str
    fetched_at: datetime
    price: PriceSnapshot
    fundamentals: Fundamentals
    sentiment: SentimentScore
    technical_signals: list[str] = Field(default_factory=list)
    anomalies: list[str] = Field(default_factory=list)


class Alert(BaseModel):
    id: str
    ticker: str
    condition_expr: str
    notify_via: list[str] = Field(default_factory=list)
    created_at: datetime
    last_triggered: datetime | None = None
    trigger_count: int = 0


class AnalysisReport(BaseModel):
    ticker: str
    generated_at: datetime
    depth: str
    summary: str
    bull_case: str
    bear_case: str
    key_risks: list[str]
    price_target_range: tuple[float, float] | None = None
    signals: list[str]
    raw_data: MarketSnapshot
