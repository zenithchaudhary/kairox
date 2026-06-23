from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.models import User, Watchlist, Instrument

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class InstrumentResponse(BaseModel):
    id: UUID
    ticker: str
    name: str
    asset_class: str
    exchange: str

    class Config:
        from_attributes = True


class WatchlistItemResponse(BaseModel):
    id: UUID
    instrument: InstrumentResponse
    created_at: datetime

    class Config:
        from_attributes = True


class AddToWatchlistRequest(BaseModel):
    instrument_id: UUID


def _get_user(firebase_uid: str, db: Session) -> User:
    """
    Helper to look up the DB user from a firebase_uid.
    Raises 404 if user has never called /auth/register — they must
    register first before accessing protected features.
    """
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Call /auth/register first.",
        )
    return user


@router.get("", response_model=list[WatchlistItemResponse])
def get_watchlist(
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all watchlist items for the current user."""
    user = _get_user(firebase_uid, db)
    return db.query(Watchlist).filter(Watchlist.user_id == user.id).all()


@router.post("", response_model=WatchlistItemResponse, status_code=201)
def add_to_watchlist(
    body: AddToWatchlistRequest,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add an instrument to the current user's watchlist."""
    user = _get_user(firebase_uid, db)

    # Verify the instrument exists
    instrument = db.query(Instrument).filter(
        Instrument.id == body.instrument_id
    ).first()
    if not instrument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instrument not found.",
        )

    # Check for duplicates — don't add the same instrument twice
    existing = db.query(Watchlist).filter(
        Watchlist.user_id == user.id,
        Watchlist.instrument_id == body.instrument_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Instrument already on watchlist.",
        )

    item = Watchlist(user_id=user.id, instrument_id=body.instrument_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{watchlist_item_id}", status_code=204)
def remove_from_watchlist(
    watchlist_item_id: UUID,
    firebase_uid: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove an instrument from the current user's watchlist."""
    user = _get_user(firebase_uid, db)

    item = db.query(Watchlist).filter(
        Watchlist.id == watchlist_item_id,
        Watchlist.user_id == user.id,
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )

    db.delete(item)
    db.commit()