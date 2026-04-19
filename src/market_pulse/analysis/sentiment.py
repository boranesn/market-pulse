"""Sentiment analysis: VADER on news + LLM-summarized themes."""
from __future__ import annotations


def score_text(text: str) -> float:
    """Return VADER compound score [-1, 1] for a piece of text."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    return SentimentIntensityAnalyzer().polarity_scores(text)["compound"]


def score_articles(articles: list[dict[str, object]]) -> tuple[float, int]:
    """Return (avg_score, count) for a list of news article dicts."""
    scores = []
    for a in articles:
        title = str(a.get("title") or "")
        desc = str(a.get("description") or "")
        scores.append(score_text(f"{title}. {desc}"))
    if not scores:
        return 0.0, 0
    return sum(scores) / len(scores), len(scores)


def score_reddit(posts: list[dict[str, object]]) -> tuple[float, int]:
    scores = [score_text(str(p.get("title") or "")) for p in posts]
    if not scores:
        return 0.0, 0
    return sum(scores) / len(scores), len(scores)


def combined_sentiment(
    news_articles: list[dict[str, object]],
    reddit_posts: list[dict[str, object]],
    news_weight: float = 0.6,
    reddit_weight: float = 0.4,
) -> dict[str, object]:
    news_score, news_count = score_articles(news_articles)
    reddit_score, reddit_count = score_reddit(reddit_posts)
    total = news_weight + reddit_weight
    combined = (news_score * news_weight + reddit_score * reddit_weight) / total
    return {
        "score": round(combined, 4),
        "news_score": round(news_score, 4),
        "reddit_score": round(reddit_score, 4),
        "news_count": news_count,
        "reddit_count": reddit_count,
    }
