from sqlalchemy.orm import Session
from src.models import Article
from src.ingestion.scraper import scrape_article
from src.analysis.article_analyzer import analyze_article, condense_for_analysis


def run_analysis(db: Session) -> None:
    """
    Finds canonical articles (not duplicates) that haven't been
    analyzed yet, and runs scrape -> condense -> analyze -> save
    for each one.
    """
    articles = (
        db.query(Article)
        .filter(Article.duplicate_of_id.is_(None))
        .filter(Article.grok_summary.is_(None))
        .all()
    )

    print(f"Found {len(articles)} articles to analyze")

    analyzed = 0
    failed = 0

    for article in articles:
        try:
            _analyze_one(db, article)
            analyzed += 1
        except Exception as e:
            # One bad article (scraping edge case, API error, etc.)
            # should not stop the rest of the batch. Block 23 adds
            # real retry logic, for now we skip and move on.
            print(f"Failed to analyze {article.id}: {e}")
            failed += 1

    print(f"Analyzed {analyzed}, failed {failed}")


def _analyze_one(db: Session, article: Article) -> None:
    source_name = article.source.name

    full_text = scrape_article(article.url)

    if full_text:
        body = condense_for_analysis(full_text, source_name)
    else:
        body = f"Source: {source_name}\n\n{article.body or ''}"

    result = analyze_article(article.headline, body)

    article.full_text = full_text
    article.grok_summary = result.summary
    article.suggested_angle = result.suggested_angle
    article.relevance_score = result.relevance_score

    db.commit()