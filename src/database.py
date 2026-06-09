from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Read the database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
# This is the connection pool to PostgreSQL

engine = create_engine(DATABASE_URL)

# Create a session factory
# Each session to FASTAPI gets one session from this factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all SQLAlchemy models
# Every table model will inherit from this
class Base(DeclarativeBase):
    pass


# Dependency for FASTAPI routes
# Yields a database session and closes it when the request is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        