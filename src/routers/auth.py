from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from firebase_admin import auth as firebase_auth

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class UserResponse(BaseModel):
    # UUID type here instead of str — Pydantic serializes UUID to
    # a string in JSON automatically, so the API response is still
    # a plain string. Declaring it as str causes a type mismatch
    # because SQLAlchemy returns a UUID object, not a string.
    id: UUID
    email: str
    name: str | None
    notifications_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse)
def register(
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a new user on first login or returns the existing user
    on subsequent logins. Called by the web client immediately after
    Firebase sign-in to sync the Firebase identity with our database.

    Upsert pattern: check if firebase_uid exists in DB.
    If yes — update last_login_at, return existing record.
    If no  — fetch email and name from Firebase, create new record.
    """
    existing_user = db.query(User).filter(
        User.firebase_uid == firebase_uid
    ).first()

    if existing_user:
        # Returning user — update last seen timestamp
        existing_user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing_user)
        return existing_user

    # First login — fetch email and name from Firebase
    firebase_user = firebase_auth.get_user(firebase_uid)

    new_user = User(
        firebase_uid=firebase_uid,
        email=firebase_user.email,
        name=firebase_user.display_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user