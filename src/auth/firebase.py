import os
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()


def _initialize_firebase() -> None:
    """
    Initialises the Firebase Admin SDK using the service account file.
    Called once at import time. Skips silently if already initialised,
    which prevents the 'App already exists' error on hot reloads.
    """
    if not firebase_admin._apps:
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)


# Initialise immediately when this module is imported.
# Any module that imports from src.auth.firebase triggers this.
_initialize_firebase()


def verify_token(token: str) -> str:
    """
    Verifies a Firebase ID token and returns the firebase_uid.
    Raises HTTP 401 if the token is invalid, expired, or revoked.
    The firebase_uid is the link between Firebase Auth and our
    PostgreSQL users table (Decision #12).
    """
    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )