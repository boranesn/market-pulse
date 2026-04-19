# market-pulse

> An async, LLM-powered financial market intelligence CLI that aggregates multi-source data, detects anomalies, and generates analyst-grade reports — all from your terminal.

---

## 🎯 What It Does

Most retail investors and analysts juggle 10 different tabs: price charts, news feeds, SEC filings, Reddit sentiment, earnings transcripts. `market-pulse` collapses all of this into a single terminal-native tool with structured AI analysis.

```bash
# Example usage
pulse watch AAPL MSFT NVDA --interval 60
pulse report TSLA --depth full --format pdf
pulse scan --sector "semiconductor" --signal "earnings_beat"
pulse compare AMZN GOOG --metric revenue_growth --years 3
pulse alert add NVDA --condition "price > 200-day-MA" --notify slack
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.12+ | Match expressions, tomllib, improved typing |
| Async runtime | `asyncio` + `aiohttp` | Concurrent API calls across 5+ data sources |
| Data processing | `DuckDB` + `Polars` | Columnar analytics without Spark overhead |
| LLM layer | Anthropic Claude API | Structured output via tool use |
| CLI | `Typer` + `Rich` | Beautiful terminal UIs, zero boilerplate |
| Validation | `Pydantic v2` | Schema validation + settings management |
| Scheduling | `APScheduler` | Watch mode & alert polling |
| Caching | `diskcache` | Persist API responses across sessions |
| Storage | `DuckDB` (local file) | Queryable time-series without a server |
| Packaging | `uv` | Fast, modern Python package manager |
| Testing | `pytest-asyncio` + `respx` | Async test support + HTTP mocking |
| Linting | `Ruff` + `mypy` | Modern linter, strict type checking |

---

## 📁 Repository Structure

```
market-pulse/
├── src/
│   └── market_pulse/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py              # Typer root app + subcommand registration
│       │   ├── watch.py            # `pulse watch` command
│       │   ├── report.py           # `pulse report` command
│       │   ├── scan.py             # `pulse scan` command
│       │   ├── compare.py          # `pulse compare` command
│       │   └── alert.py            # `pulse alert` command
│       ├── data/
│       │   ├── __init__.py
│       │   ├── sources/
│       │   │   ├── yahoo.py        # Yahoo Finance (yfinance) — price & fundamentals
│       │   │   ├── alphaV.py       # Alpha Vantage — technicals & earnings
│       │   │   ├── newsapi.py      # NewsAPI — sentiment input
│       │   │   ├── sec.py          # SEC EDGAR — 10-K/10-Q filings
│       │   │   └── reddit.py       # Reddit PRAW — retail sentiment
│       │   ├── aggregator.py       # Async fan-out: fetch all sources concurrently
│       │   └── normalizer.py       # Unify schemas across sources → MarketSnapshot
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── technical.py        # SMA, EMA, RSI, MACD, Bollinger — pure Polars
│       │   ├── fundamental.py      # P/E, EV/EBITDA, DCF estimate, growth rates
│       │   ├── sentiment.py        # News + Reddit → sentiment score (VADER + LLM)
│       │   ├── anomaly.py          # Z-score & IQR based anomaly detection on price/volume
│       │   └── comparison.py       # Peer comparison & relative strength
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── analyst.py          # Claude tool-use: structured investment analysis
│       │   ├── summarizer.py       # Summarize SEC filings & earnings transcripts
│       │   ├── scanner.py          # LLM-powered signal detection from news
│       │   └── prompts.py          # All prompt templates (no inline strings)
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── db.py               # DuckDB connection manager (async-safe)
│       │   ├── migrations/
│       │   │   └── 001_initial.sql # Schema: snapshots, alerts, reports
│       │   └── cache.py            # diskcache wrapper with TTL presets
│       ├── alerts/
│       │   ├── __init__.py
│       │   ├── engine.py           # Alert evaluation loop (APScheduler)
│       │   ├── conditions.py       # DSL parser: "price > 200-day-MA"
│       │   └── notifiers/
│       │       ├── slack.py        # Slack webhook notifier
│       │       ├── email.py        # SMTP notifier
│       │       └── terminal.py     # Rich console notifier (default)
│       ├── export/
│       │   ├── __init__.py
│       │   ├── markdown.py         # Markdown report renderer
│       │   ├── pdf.py              # Markdown → PDF via weasyprint
│       │   └── json.py             # Structured JSON export
│       ├── models/
│       │   └── __init__.py
│       │   └── market.py           # Pydantic v2 models: MarketSnapshot, Signal, Alert, Report
│       └── config.py               # Pydantic BaseSettings — reads .env / pyproject.toml
├── tests/
│   ├── conftest.py
│   ├── data/
│   │   ├── test_yahoo.py
│   │   ├── test_aggregator.py
│   │   └── fixtures/               # Static JSON responses for mocking
│   ├── analysis/
│   │   ├── test_technical.py
│   │   ├── test_fundamental.py
│   │   └── test_anomaly.py
│   ├── ai/
│   │   └── test_analyst.py
│   └── alerts/
│       └── test_conditions.py
├── pyproject.toml                  # uv-managed, all deps here
├── .env.example
├── .gitignore
├── ruff.toml
├── mypy.ini
└── README.md
```

---

## 🔬 Core Data Models (`src/market_pulse/models/market.py`)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal

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
    pe_ratio: float | None
    ev_ebitda: float | None
    revenue_growth_yoy: float | None
    gross_margin: float | None
    debt_to_equity: float | None
    free_cash_flow: int | None
    eps_surprise_pct: float | None

class SentimentScore(BaseModel):
    ticker: str
    score: float          # -1.0 to 1.0
    confidence: float     # 0.0 to 1.0
    news_count: int
    reddit_mentions: int
    dominant_theme: str   # e.g. "earnings beat", "product recall"

class MarketSnapshot(BaseModel):
    ticker: str
    fetched_at: datetime
    price: PriceSnapshot
    fundamentals: Fundamentals
    sentiment: SentimentScore
    technical_signals: list[str]   # e.g. ["RSI oversold", "Death cross"]
    anomalies: list[str]

class Alert(BaseModel):
    id: str
    ticker: str
    condition_expr: str   # e.g. "price > 200-day-MA"
    notify_via: list[str]
    created_at: datetime
    last_triggered: datetime | None = None
    trigger_count: int = 0

class AnalysisReport(BaseModel):
    ticker: str
    generated_at: datetime
    depth: str             # "quick" | "standard" | "full"
    summary: str
    bull_case: str
    bear_case: str
    key_risks: list[str]
    price_target_range: tuple[float, float] | None
    signals: list[str]
    raw_data: MarketSnapshot
```

---

## 🤖 AI Layer (`src/market_pulse/ai/analyst.py`)

Uses Claude's **tool use** feature to force structured JSON output from analysis — never raw text parsing.

```python
# Claude is given tools that define the exact output schema.
# It must call generate_analysis() with structured args — no free-form text.

ANALYSIS_TOOLS = [
    {
        "name": "generate_analysis",
        "description": "Generate a structured investment analysis",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "bull_case": {"type": "string"},
                "bear_case": {"type": "string"},
                "key_risks": {"type": "array", "items": {"type": "string"}},
                "price_target_range": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2
                },
                "signals": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["summary", "bull_case", "bear_case", "key_risks", "signals"]
        }
    }
]
```

---

## ⚡ Async Data Aggregator (`src/market_pulse/data/aggregator.py`)

```python
async def fetch_all(ticker: str) -> MarketSnapshot:
    async with asyncio.TaskGroup() as tg:
        price_task = tg.create_task(yahoo.fetch_price(ticker))
        fund_task = tg.create_task(alphav.fetch_fundamentals(ticker))
        news_task = tg.create_task(newsapi.fetch_sentiment(ticker))
        sec_task = tg.create_task(sec.fetch_latest_filing(ticker))
        reddit_task = tg.create_task(reddit.fetch_mentions(ticker))
    # All 5 sources fetched concurrently — total latency = slowest source, not sum
```

Uses Python 3.11+ `TaskGroup` for structured concurrency with automatic error propagation.

---

## 📊 DuckDB Storage Schema

```sql
-- migrations/001_initial.sql
CREATE TABLE snapshots (
    ticker VARCHAR,
    fetched_at TIMESTAMPTZ,
    close_price DECIMAL(10,4),
    volume BIGINT,
    pe_ratio FLOAT,
    sentiment_score FLOAT,
    anomalies JSON,
    raw JSON,
    PRIMARY KEY (ticker, fetched_at)
);

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR NOT NULL,
    condition_expr VARCHAR NOT NULL,
    notify_via JSON,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_triggered TIMESTAMPTZ,
    trigger_count INT DEFAULT 0
);

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    depth VARCHAR,
    content JSON
);
```

DuckDB allows running complex analytical queries (rolling averages, percentile ranks, joins) directly on the local file — no PostgreSQL server needed.

---

## 🖥️ CLI Output Examples (Rich)

**`pulse watch AAPL NVDA`**
```
┌─────────────────────────────────────────┐
│  market-pulse  ·  Live Watch  ·  14:32  │
├──────┬────────┬────────┬───────┬────────┤
│ TICK │ PRICE  │ CHG    │ SENT  │ SIGNAL │
├──────┼────────┼────────┼───────┼────────┤
│ AAPL │ 189.42 │ +1.2%  │ 0.62  │ RSI ↑  │
│ NVDA │ 875.10 │ -0.4%  │ 0.81  │ Vol ⚠  │
└──────┴────────┴────────┴───────┴────────┘
  Refreshing in 58s  ·  Press q to quit
```

**`pulse report TSLA --depth full`**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TSLA — Full Analysis Report  2024-01-15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Summary
 Tesla's Q4 deliveries missed consensus by 4.2%,
 compressing margin expectations. However, FSD
 progress and energy segment growth offset concerns...

 Bull Case  ▸ FSD monetization at scale
            ▸ Energy storage 127% YoY growth
            ▸ New model cycle in H2 2024

 Bear Case  ▸ EV price war intensifying
            ▸ CEO distraction risk
            ▸ China competition (BYD)

 Key Risks  ⚠ Regulatory: FSD safety investigations
            ⚠ Macro: High rates compress EV demand
            ⚠ Execution: Cybertruck ramp uncertainty

 Price Target  $165 – $240  (current: $189)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📦 Phases

### Phase 1 — Project Setup (Day 1)
- [ ] Init with `uv init market-pulse`
- [ ] `pyproject.toml` with all dependencies
- [ ] `ruff.toml` and `mypy.ini` configured to strict
- [ ] `config.py` with Pydantic BaseSettings
- [ ] `models/market.py` — all Pydantic models
- [ ] `storage/db.py` — DuckDB connection + migration runner
- [ ] `migrations/001_initial.sql`
- [ ] `storage/cache.py` — diskcache wrapper
- [ ] Typer app skeleton (`cli/app.py`) that prints version
- [ ] `tests/conftest.py` with DuckDB in-memory fixture
- [ ] Git: `feat: project foundation`

### Phase 2 — Data Sources (Day 2)
- [ ] `data/sources/yahoo.py` — price + fundamentals via yfinance
- [ ] `data/sources/alphaV.py` — technicals via Alpha Vantage
- [ ] `data/sources/newsapi.py` — headlines fetch
- [ ] `data/sources/reddit.py` — PRAW mention scraper
- [ ] `data/sources/sec.py` — EDGAR filing fetcher (latest 10-K/10-Q)
- [ ] `data/aggregator.py` — TaskGroup concurrent fetch
- [ ] `data/normalizer.py` — map all sources → MarketSnapshot
- [ ] Tests with `respx` HTTP mocking + JSON fixtures
- [ ] Git: `feat: data source layer`

### Phase 3 — Analysis Engine (Day 3)
- [ ] `analysis/technical.py` — RSI, MACD, SMA(20/50/200), Bollinger, volume spike
- [ ] `analysis/fundamental.py` — P/E, EV/EBITDA, DCF (simple), growth rates
- [ ] `analysis/sentiment.py` — VADER on news + LLM summary of themes
- [ ] `analysis/anomaly.py` — Z-score on price/volume, flag outliers
- [ ] `analysis/comparison.py` — peer relative strength, sector rank
- [ ] Unit tests for each analysis module (pure functions — easy to test)
- [ ] Git: `feat: analysis engine`

### Phase 4 — AI Layer (Day 4)
- [ ] `ai/prompts.py` — all prompt templates as constants
- [ ] `ai/analyst.py` — Claude tool-use for structured investment analysis
- [ ] `ai/summarizer.py` — SEC filing & earnings transcript summarization
- [ ] `ai/scanner.py` — news signal detection (identify catalysts)
- [ ] `ai/` tests with mocked Anthropic API responses
- [ ] Git: `feat: AI analysis layer`

### Phase 5 — CLI Commands (Day 5)
- [ ] `cli/watch.py` — Live dashboard with Rich Live + APScheduler
- [ ] `cli/report.py` — Full report generation + MD/PDF export
- [ ] `cli/scan.py` — Sector scan for signals
- [ ] `cli/compare.py` — Side-by-side peer comparison table
- [ ] `cli/alert.py` — CRUD for alerts + condition DSL parser
- [ ] `alerts/engine.py` — Background polling loop
- [ ] `alerts/notifiers/` — Slack, email, terminal
- [ ] Git: `feat: CLI commands and alert engine`

### Phase 6 — Polish (Day 6)
- [ ] `export/pdf.py` — weasyprint PDF generation
- [ ] Integration tests: run full `pulse report` flow end-to-end
- [ ] Coverage ≥ 75%
- [ ] README with GIF demo, installation, all commands
- [ ] `.env.example`
- [ ] Git: `docs: complete documentation`
- [ ] Tag: `v1.0.0`

---

## 🔑 What This Demonstrates

- **Async Python mastery** — TaskGroup, aiohttp, APScheduler
- **Modern data stack** — DuckDB + Polars instead of Pandas/SQLite
- **LLM tool use** — Structured output via Claude tool calling (not prompt hacking)
- **Production CLI design** — Rich, Typer, real UX
- **Multi-source data aggregation** — 5 async sources unified by Pydantic
- **Financial domain knowledge** — RSI, DCF, EV/EBITDA, sentiment scoring

---

*Built with Python 3.12 · DuckDB · Polars · Anthropic Claude · Typer · Rich · uv*
