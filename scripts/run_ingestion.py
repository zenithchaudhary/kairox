from src.database import SessionLocal
from src.ingestion.worker import run_ingestion

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Starting ingestion...")
        run_ingestion(db)
        print("Done.")
    finally:
        db.close()