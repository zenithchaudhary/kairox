from sqlalchemy.orm import Session
from src.models import Article
from src.ingestion.scraper import scrape_article
from src.analysis.article_analyzer import analyze_article, condense_for_analysis


def run_analysis(db: Session) -> None:
    """
    Finds canonical articles (not duplicates) that haven't been
    analyzed yet, and runs scrape -> condense -> analyze -> save
    for each one. Safe to interrupt and rerun: each article commits
    individually, and already-analyzed articles are skipped on the
    next run via the grok_summary IS NULL filter.
    """
    articles = (
        db.query(Article)
        .filter(Article.duplicate_of_id.is_(None))
        .filter(Article.grok_summary.is_(None))
        .all()
    )

    total = len(articles)
    print(f"Found {total} articles to analyze")

    analyzed = 0
    failed = 0

    for i, article in enumerate(articles, start=1):
        print(f"[{i}/{total}] {article.headline[:60]}")
        try:
            _analyze_one(db, article)
            analyzed += 1
        except Exception as e:
            print(f"  Failed: {e}")
            failed += 1

    print(f"\nAnalyzed {analyzed}, failed {failed}")


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