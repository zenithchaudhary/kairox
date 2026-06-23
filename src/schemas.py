from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


# ── Source schemas ──────────────────────────────────────────

class SourceMinimal(BaseModel):
    """Minimal source info nested inside article responses."""
    id: UUID
    name: str
    tier: int

    class Config:
        from_attributes = True


class SourceCreate(BaseModel):
    """What the API receives when creating a source."""
    name: str
    url: str
    category: str
    tier: int
    source_type: str


class SourceResponse(BaseModel):
    """What the API returns when showing a source."""
    id: UUID
    name: str
    url: str
    category: str
    tier: int
    source_type: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Article schemas ─────────────────────────────────────────

class ArticleCreate(BaseModel):
    """What the API receives when creating an article manually."""
    headline: str
    url: Optional[str] = None
    relevance_score: Optional[int] = None
    editorial_status: Optional[str] = "draft"


class ArticleResponse(BaseModel):
    """
    What the API returns when showing an article.
    Includes Grok-generated fields and nested source info.
    """
    id: UUID
    headline: str
    url: Optional[str]
    body: Optional[str]
    published_at: Optional[datetime]
    grok_summary: Optional[str]
    suggested_angle: Optional[str]
    relevance_score: Optional[int]
    editorial_status: str
    duplicate_of_id: Optional[UUID]
    created_at: datetime
    # Nested source — populated via joinedload in the endpoint
    source: Optional[SourceMinimal] = None

    class Config:
        from_attributes = True