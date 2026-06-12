from datetime import datetime, timezone
from sqlalchemy import select
from src.database import SessionLocal
from src.models import Article, Embedding, Source
from src.ingestion.embeddings import generate_embedding
from src.ingestion.deduplication import find_duplicate

db = SessionLocal()

# Use any existing source for this test
source = db.query(Source).first()

now = datetime.now(timezone.utc)

# Two articles describing the same event in different words.
# These should be detected as duplicates.
headline_a = "Fed holds interest rates steady amid inflation concerns"
headline_b = "Federal Reserve keeps rates unchanged, citing inflation"

# An unrelated article. Should NOT be flagged as a duplicate of A.
headline_c = "Tesla recalls 50,000 vehicles over battery issue"

vector_a = generate_embedding(headline_a, "")
vector_b = generate_embedding(headline_b, "")
vector_c = generate_embedding(headline_c, "")

# Insert article A as if it already exists in the database
article_a = Article(
    source_id=source.id,
    headline=headline_a,
    url="https://test.local/article-a",
    body="",
    published_at=now,
)
db.add(article_a)
db.flush()

embedding_a = Embedding(article_id=article_a.id, embedding=vector_a)
db.add(embedding_a)
db.commit()

# DEBUG: distance between B and A
debug_result_b = db.execute(
    select(
        Article,
        Embedding.embedding.cosine_distance(vector_b).label("distance")
    )
    .join(Embedding, Embedding.article_id == Article.id)
    .order_by("distance")
    .limit(1)
).first()

if debug_result_b:
    debug_article_b, debug_distance_b = debug_result_b
    print(f"DEBUG - Distance B vs A: {debug_distance_b}")
else:
    print("DEBUG - No rows found for B")

# DEBUG: distance between C and A
debug_result_c = db.execute(
    select(
        Article,
        Embedding.embedding.cosine_distance(vector_c).label("distance")
    )
    .join(Embedding, Embedding.article_id == Article.id)
    .order_by("distance")
    .limit(1)
).first()

if debug_result_c:
    debug_article_c, debug_distance_c = debug_result_c
    print(f"DEBUG - Distance C vs A: {debug_distance_c}")
else:
    print("DEBUG - No rows found for C")

# Now check: does article B (similar wording) get matched to A?
match_b = find_duplicate(db, vector_b, now)
print(f"Article B match: {match_b.headline if match_b else None}")

# And does article C (unrelated) get matched to anything?
match_c = find_duplicate(db, vector_c, now)
print(f"Article C match: {match_c.headline if match_c else None}")

# Cleanup
db.delete(embedding_a)
db.delete(article_a)
db.commit()
db.close()