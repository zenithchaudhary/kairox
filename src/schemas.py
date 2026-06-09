from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


# ── Source schemas ──────────────────────────────────────────

class SourceCreate(BaseModel):
    """What the API receives when creating a source."""
    name: str
    url: str
    category: str


class SourceResponse(BaseModel):
    """What the API returns when showing a source."""
    id: UUID
    name: str
    url: str
    category: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Article schemas ─────────────────────────────────────────

class ArticleCreate(BaseModel):
    """What the API receives when creating an article."""
    headline: str
    url: Optional[str] = None
    relevance_score: Optional[int] = None
    editorial_status: Optional[str] = "draft"


class ArticleResponse(BaseModel):
    """What the API returns when showing an article."""
    id: UUID
    headline: str
    url: Optional[str]
    relevance_score: Optional[int]
    editorial_status: str
    publish_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True