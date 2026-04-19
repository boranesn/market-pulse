"""All prompt templates as module-level constants — no inline strings in AI modules."""

ANALYST_SYSTEM = """\
You are a senior equity research analyst with deep expertise in financial modeling, \
technical analysis, and macroeconomic context. You produce structured, concise, \
data-driven investment analyses. Always cite specific metrics from the data provided. \
Never fabricate numbers. If data is unavailable, say so explicitly."""

ANALYST_USER = """\
Analyze the following market data for {ticker} and generate a structured investment analysis.

## Price Data
- Current Price: ${close}
- Volume: {volume:,}
- VWAP: ${vwap}

## Fundamentals
- P/E Ratio: {pe_ratio}
- EV/EBITDA: {ev_ebitda}
- Revenue Growth (YoY): {revenue_growth}
- Gross Margin: {gross_margin}
- Debt/Equity: {debt_to_equity}
- Free Cash Flow: ${free_cash_flow}
- EPS Surprise: {eps_surprise}%

## Technical Signals
{technical_signals}

## Sentiment
- Score: {sentiment_score} (range -1 to +1)
- News Articles Analyzed: {news_count}
- Reddit Mentions: {reddit_mentions}
- Dominant Theme: {dominant_theme}

## Anomalies
{anomalies}

Analysis depth: {depth}

Call the generate_analysis tool with your structured analysis."""

SUMMARIZER_SYSTEM = """\
You are a financial document analyst. Summarize SEC filings and earnings transcripts \
into clear, actionable key points. Focus on: revenue trends, margin changes, guidance, \
risk factors, and management tone. Be concise — 3-5 bullet points per section."""

SUMMARIZER_USER = """\
Summarize the following {doc_type} for {ticker}:

{content}

Extract: key financial metrics, forward guidance, major risks, and management commentary."""

SCANNER_SYSTEM = """\
You are a market signal detection system. Analyze news headlines and identify \
actionable trading signals. Classify signals as: earnings_beat, earnings_miss, \
product_launch, regulatory_risk, acquisition, insider_activity, analyst_upgrade, \
analyst_downgrade, macro_risk, or other."""

SCANNER_USER = """\
Analyze these news headlines for {ticker} in sector {sector} and identify trading signals.

Headlines:
{headlines}

For each signal found, provide: signal_type, confidence (0-1), and a brief explanation."""
