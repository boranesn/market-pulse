from datetime import datetime

from market_pulse.models.market import Fundamentals, MarketSnapshot, PriceSnapshot, SentimentScore


def normalize(
    ticker: str,
    fetched_at: datetime,
    price: PriceSnapshot,
    fundamentals: Fundamentals,
    news_articles: list[dict[str, object]],
    sec_filing: dict[str, object],
    reddit_posts: list[dict[str, object]],
) -> MarketSnapshot:
    sentiment = _compute_sentiment(ticker, news_articles, reddit_posts)
    return MarketSnapshot(
        ticker=ticker,
        fetched_at=fetched_at,
        price=price,
        fundamentals=fundamentals,
        sentiment=sentiment,
        technical_signals=[],
        anomalies=[],
    )


def _compute_sentiment(
    ticker: str,
    news_articles: list[dict[str, object]],
    reddit_posts: list[dict[str, object]],
) -> SentimentScore:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()
    scores: list[float] = []

    for article in news_articles:
        title = str(article.get("title", "") or "")
        description = str(article.get("description", "") or "")
        text = f"{title}. {description}"
        compound = analyzer.polarity_scores(text)["compound"]
        scores.append(compound)

    for post in reddit_posts:
        title = str(post.get("title", "") or "")
        compound = analyzer.polarity_scores(title)["compound"]
        scores.append(compound)

    avg_score = sum(scores) / len(scores) if scores else 0.0
    confidence = min(1.0, len(scores) / 20.0)

    return SentimentScore(
        ticker=ticker,
        score=round(avg_score, 4),
        confidence=round(confidence, 4),
        news_count=len(news_articles),
        reddit_mentions=len(reddit_posts),
        dominant_theme="",
    )
