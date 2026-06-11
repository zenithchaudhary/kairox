from src.ingestion.rss_fetcher import fetch_feed, RSS_SOURCES

if __name__ == "__main__":
    for name, url in RSS_SOURCES.items():
        print(f"\n=== {name} ===")
        articles = fetch_feed(url)
        print(f"Fetched {len(articles)} articles")
        if articles:
            print(f"First: {articles[0]['title']}")
            print(f"URL:   {articles[0]['url']}")
            print(f"Date:  {articles[0]['published_at']}")
            