from src.database import SessionLocal
from src.models import Article
from src.ingestion.scraper import scrape_article

if __name__ == "__main__":
    db = SessionLocal()

    # Grab a few real articles already in the database to test against
    articles = db.query(Article).limit(5).all()

    for article in articles:
        text = scrape_article(article.url)

        print(f"\n=== {article.headline[:60]} ===")
        if text:
            print(f"Scraped {len(text)} characters")
            print(f"Preview: {text[:200]}")
        else:
            print("Scraping failed, would fall back to RSS snippet")

    db.close()