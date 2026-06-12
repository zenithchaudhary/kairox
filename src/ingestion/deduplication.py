from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models import Article, Embedding

# Cosine distance threshold. Below this, two articles are considered
# the same story. Tuned empirically: same-story headlines with different
# wording measured at ~0.30, unrelated headlines at ~0.70. 0.35 sits
# safely between the two.
SIMILARITY_THRESHOLD = 0.35

# Only compare against articles published within this window.
# Prevents matching unrelated stories that happen to use similar language.
DEDUP_WINDOW_HOURS = 48


def find_duplicate(db: Session, embedding: list[float], published_at: datetime | None) -> Article | None:
    """
    Given a new article's embedding, check if a similar article already
    exists in the recent window. Returns the matching Article if its
    cosine distance is within SIMILARITY_THRESHOLD, otherwise None.
    """
    if published_at is None:
        published_at = datetime.now(timezone.utc)

    window_start = published_at - timedelta(hours=DEDUP_WINDOW_HOURS)

    # <=> is pgvector's cosine distance operator: 0 = identical, 2 = opposite.
    result = db.execute(
        select(
            Article,
            Embedding.embedding.cosine_distance(embedding).label("distance")
        )
        .join(Embedding, Embedding.article_id == Article.id)
        .where(Article.published_at >= window_start)
        .order_by("distance")
        .limit(1)
    ).first()

    if result is None:
        return None

    matched_article, distance = result

    if distance <= SIMILARITY_THRESHOLD:
        return matched_article

    return None