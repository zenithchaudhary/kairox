from src.database import SessionLocal
from src.models import Article, Source
from src.ingestion.scraper import scrape_article
from src.analysis.article_analyzer import analyze_article, condense_for_analysis

if __name__ == "__main__":
    db = SessionLocal()

    sources = db.query(Source).filter(Source.active == True).all()

    for source in sources:
        # Skip duplicates, only canonical articles need analysis
        article = (
            db.query(Article)
            .filter(Article.source_id == source.id)
            .filter(Article.duplicate_of_id.is_(None))
            .first()
        )

        if article is None:
            print(f"\n=== {source.name}: no articles found ===")
            continue

        full_text = scrape_article(article.url)

        if full_text:
            body = condense_for_analysis(full_text, source.name)
            scrape_status = "scraped"
        else:
            body = f"Source: {source.name}\n\n{article.body or ''}"
            scrape_status = "fallback to RSS snippet"

        print(f"\n=== {source.name} ({scrape_status}) ===")
        print(f"Headline: {article.headline}")

        result = analyze_article(article.headline, body)

        print(f"Summary: {result.summary}")
        print(f"Suggested angle: {result.suggested_angle}")
        print(f"Relevance score: {result.relevance_score}")

    db.close()