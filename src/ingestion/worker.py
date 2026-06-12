from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.models import Source, Article, IngestionRun, Embedding
from src.ingestion.rss_fetcher import fetch_feed
from src.ingestion.embeddings import generate_embedding
from src.ingestion.deduplication import find_duplicate


def run_ingestion(db: Session) -> None:
    sources = db.query(Source).filter(Source.active == True).all()

    for source in sources:
        _ingest_source(db, source)


def _ingest_source(db: Session, source: Source) -> None:
    run = IngestionRun(
        source_id=source.id,
        started_at=datetime.now(timezone.utc),
        status="running",
    )
    db.add(run)
    db.commit()

    try:
        articles = fetch_feed(source.url)

        articles_found = len(articles)
        articles_new = 0

        for article_data in articles:
            exists = db.query(Article).filter(
                Article.url == article_data["url"]
            ).first()

            if exists:
                continue

            vector = generate_embedding(article_data["title"], article_data["summary"] or "")

            # Check if this is a near-duplicate of a recently seen story
            # before we insert it. The duplicate (if any) becomes the
            # canonical article this one points to.
            duplicate = find_duplicate(db, vector, article_data["published_at"])

            article = Article(
                source_id=source.id,
                headline=article_data["title"],
                url=article_data["url"],
                body=article_data["summary"],
                published_at=article_data["published_at"],
                duplicate_of_id=duplicate.id if duplicate else None,
            )
            db.add(article)
            db.flush()

            embedding = Embedding(
                article_id=article.id,
                embedding=vector,
            )
            db.add(embedding)

            articles_new += 1

        db.commit()

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.articles_found = articles_found
        run.articles_new = articles_new
        db.commit()

    except Exception as e:
        db.rollback()
        run.status = "failed"
        run.error_message = str(e)
        run.completed_at = datetime.now(timezone.utc)
        db.commit()