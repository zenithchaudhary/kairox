from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload
from typing import List
from src.database import get_db
from src.models import Source, Article
from src.schemas import SourceCreate, SourceResponse, ArticleCreate, ArticleResponse
from src.routers import auth, watchlist
import uuid

app = FastAPI(
    title="KAIROX",
    description="AI-powered financial news intelligence platform",
    version="0.1.0"
)

# Register routers
app.include_router(auth.router)
app.include_router(watchlist.router)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """Serve the KAIROX web interface."""
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
def health():
    return {"status": "healthy"}


# ── Source routes ────────────────────────────────────────────

@app.get("/sources", response_model=List[SourceResponse])
def get_sources(db: Session = Depends(get_db)):
    """Return all RSS sources."""
    return db.query(Source).all()


@app.post("/sources", response_model=SourceResponse, status_code=201)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """Add a new RSS source."""
    db_source = Source(
        id=uuid.uuid4(),
        name=source.name,
        url=source.url,
        category=source.category,
        tier=source.tier,
        source_type=source.source_type,
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


# ── Article routes ───────────────────────────────────────────

@app.get("/articles", response_model=List[ArticleResponse])
def get_articles(db: Session = Depends(get_db)):
    """
    Return canonical articles sorted by relevance then recency.
    Excludes duplicates. Eager-loads source so the nested source
    object is available in the response without extra queries.
    """
    return (
        db.query(Article)
        .options(joinedload(Article.source))
        .filter(Article.duplicate_of_id.is_(None))
        .order_by(
            Article.relevance_score.desc().nullslast(),
            Article.published_at.desc().nullslast(),
        )
        .all()
    )


@app.post("/articles", response_model=ArticleResponse, status_code=201)
def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    """Create a new article manually."""
    db_article = Article(
        id=uuid.uuid4(),
        headline=article.headline,
        url=article.url,
        relevance_score=article.relevance_score,
        editorial_status=article.editorial_status or "draft"
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article