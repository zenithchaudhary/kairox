import uuid
from datetime import datetime
from sqlalchemy import (
    String, Boolean, Integer, Text,
    DateTime, Date, Numeric, ForeignKey, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import func
from database import Base


class Source(Base):
    __tablename__ = "sources"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = mapped_column(String, nullable=False)
    url = mapped_column(String, nullable=False)
    category = mapped_column(String, nullable=False)
    active = mapped_column(Boolean, default=True)
    created_at = mapped_column(DateTime, default=func.now())

    # Relationship — one source has many articles
    articles = relationship("Article", back_populates="source")
    ingestion_runs = relationship("IngestionRun", back_populates="source")


class Article(Base):
    __tablename__ = "articles"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id"))
    headline = mapped_column(String, nullable=False)
    body = mapped_column(Text)
    url = mapped_column(String)
    source_article_id = mapped_column(String)
    published_at = mapped_column(DateTime)
    grok_summary = mapped_column(Text)
    suggested_angle = mapped_column(Text)
    editorial_angle = mapped_column(Text)
    relevance_score = mapped_column(Integer)
    editorial_status = mapped_column(String, default="draft")
    publish_date = mapped_column(Date)
    created_at = mapped_column(DateTime, default=func.now())

    # Relationships
    source = relationship("Source", back_populates="articles")
    article_instruments = relationship("ArticleInstrument", back_populates="article")


class Instrument(Base):
    __tablename__ = "instruments"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = mapped_column(String, nullable=False)
    name = mapped_column(String, nullable=False)
    asset_class = mapped_column(String, nullable=False)
    exchange = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime, default=func.now())

    # Relationships
    article_instruments = relationship("ArticleInstrument", back_populates="instrument")
    watchlists = relationship("Watchlist", back_populates="instrument")


class ArticleInstrument(Base):
    __tablename__ = "article_instruments"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = mapped_column(UUID(as_uuid=True), ForeignKey("articles.id"))
    instrument_id = mapped_column(UUID(as_uuid=True), ForeignKey("instruments.id"))

    # Relationships
    article = relationship("Article", back_populates="article_instruments")
    instrument = relationship("Instrument", back_populates="article_instruments")


class User(Base):
    __tablename__ = "users"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firebase_uid = mapped_column(String, unique=True, nullable=False)
    email = mapped_column(String, unique=True, nullable=False)
    name = mapped_column(String)
    notifications_enabled = mapped_column(Boolean, default=True)
    created_at = mapped_column(DateTime, default=func.now())
    last_login_at = mapped_column(DateTime)

    # Relationships
    watchlists = relationship("Watchlist", back_populates="user")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    instrument_id = mapped_column(UUID(as_uuid=True), ForeignKey("instruments.id"))
    created_at = mapped_column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="watchlists")
    instrument = relationship("Instrument", back_populates="watchlists")


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id"))
    started_at = mapped_column(DateTime, default=func.now())
    completed_at = mapped_column(DateTime)
    articles_found = mapped_column(Integer, default=0)
    articles_new = mapped_column(Integer, default=0)
    status = mapped_column(String, default="running")
    error_message = mapped_column(Text)

    # Relationship
    source = relationship("Source", back_populates="ingestion_runs")