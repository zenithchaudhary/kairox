from src.database import SessionLocal
from src.analysis.worker import run_analysis

if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_analysis(db)
    finally:
        db.close()