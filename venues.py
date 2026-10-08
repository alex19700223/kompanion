from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Venue, User
from schemas import VenueCreate, VenueResponse
from security import get_current_user


router = APIRouter(prefix="/venues", tags=["venues"])


@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    venue_data: VenueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    venue = Venue(
        name=venue_data.name,
        address=venue_data.address,
        lat=venue_data.lat,
        lng=venue_data.lng,
        type=venue_data.type,
        created_by=current_user.id,
    )
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue


@router.get("", response_model=list[VenueResponse])
def list_venues(
    db: Session = Depends(get_db),
):
    venues = db.query(Venue).order_by(Venue.id.desc()).limit(100).all()
    return venues


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заведение не найдено",
        )
    return venue
