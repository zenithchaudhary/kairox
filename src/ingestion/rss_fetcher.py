import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime


RSS_SOURCES = {
    "yahoo_finance": "https://finance.yahoo.com/rss/topstories",
    "marketwatch": "https://feeds.marketwatch.com/marketwatch/topstories",
    "cnbc_finance": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "seeking_alpha": "https://seekingalpha.com/feed.xml",
}


def parse_date(date_string: str | None) -> datetime | None:
    if not date_string:
        return None
    try:
        return parsedate_to_datetime(date_string)
    except Exception:
        return None


def fetch_feed(url: str) -> list[dict]:
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries:
        article = {
            "title": entry.get("title", "").strip(),
            "url": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published_at": parse_date(entry.get("published")),
            "source_name": feed.feed.get("title", "Unknown"),
        }

        if not article["title"] or not article["url"]:
            continue

        articles.append(article)

    return articles