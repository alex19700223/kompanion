from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from math import radians, sin, cos, sqrt, atan2

from database import get_db
from models import Event, Participant, User, Venue
from schemas import EventCreate, EventResponse
from security import get_current_user


router = APIRouter(prefix="/events", tags=["events"])


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    lat1_r, lat2_r = radians(lat1), radians(lat2)
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def serialize_event(
    event: Event,
    db: Session,
    user_lat: float = None,
    user_lng: float = None,
) -> dict:
    creator = db.query(User).filter(User.id == event.creator_id).first()

    venue = None
    distance_km = None
    if event.venue_id:
        venue = db.query(Venue).filter(Venue.id == event.venue_id).first()
        if venue and venue.lat is not None and venue.lng is not None:
            if user_lat is not None and user_lng is not None:
                distance_km = round(
                    haversine(user_lat, user_lng, float(venue.lat), float(venue.lng)),
                    2,
                )

    participants_rows = (
        db.query(User)
        .join(Participant, Participant.user_id == User.id)
        .filter(Participant.event_id == event.id)
        .all()
    )

    return {
        "id": event.id,
        "creator_id": event.creator_id,
        "venue_id": event.venue_id,
        "format": event.format,
        "title": event.title,
        "description": event.description,
        "starts_at": event.starts_at,
        "max_participants": event.max_participants,
        "languages": event.languages or [],
        "topics": event.topics or [],
        "alcohol": event.alcohol,
        "status": event.status,
        "created_at": event.created_at,
        "creator": {
            "id": creator.id,
            "name": creator.name,
            "age_group": creator.age_group,
        } if creator else None,
        "venue": {
            "id": venue.id,
            "name": venue.name,
            "address": venue.address,
        } if venue else None,
        "participants": [
            {"id": u.id, "name": u.name, "age_group": u.age_group}
            for u in participants_rows
        ],
        "participants_count": len(participants_rows),
        "distance_km": distance_km,
    }


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if event_data.starts_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя создать встречу в прошлом",
        )

    if event_data.venue_id is not None:
        venue = db.query(Venue).filter(Venue.id == event_data.venue_id).first()
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заведение не найдено",
            )

    event = Event(
        creator_id=current_user.id,
        venue_id=event_data.venue_id,
        format=event_data.format,
        title=event_data.title,
        description=event_data.description,
        starts_at=event_data.starts_at,
        max_participants=event_data.max_participants,
        languages=event_data.languages,
        topics=event_data.topics,
        alcohol=event_data.alcohol,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    participant = Participant(event_id=event.id, user_id=current_user.id)
    db.add(participant)
    db.commit()

    return serialize_event(event, db)


@router.get("", response_model=list[EventResponse])
def list_events(
    when: str = "all",
    lat: float = None,
    lng: float = None,
    radius: float = None,
    db: Session = Depends(get_db),
):
    query = db.query(Event).filter(Event.status == "active")

    now = datetime.now(timezone.utc)
    if when == "today":
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)
        query = query.filter(Event.starts_at >= now, Event.starts_at <= end_of_day)
    elif when == "tomorrow":
        tomorrow = now + timedelta(days=1)
        start_of_tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_tomorrow = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)
        query = query.filter(Event.starts_at >= start_of_tomorrow, Event.starts_at <= end_of_tomorrow)
    elif when == "all":
        query = query.filter(Event.starts_at >= now)

    events = query.order_by(Event.starts_at.asc()).limit(100).all()

    result = [serialize_event(e, db, lat, lng) for e in events]

    if lat is not None and lng is not None and radius is not None:
        result = [
            e for e in result
            if e["distance_km"] is not None and e["distance_km"] <= radius
        ]
        result.sort(key=lambda e: e["distance_km"])

    return result


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    lat: float = None,
    lng: float = None,
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Встреча не найдена",
        )
    return serialize_event(event, db, lat, lng)


@router.post("/{event_id}/join", status_code=status.HTTP_200_OK)
def join_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Встреча не найдена",
        )

    if event.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Встреча уже неактивна",
        )

    existing = db.query(Participant).filter(
        Participant.event_id == event_id,
        Participant.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ты уже участник этой встречи",
        )

    count = db.query(Participant).filter(Participant.event_id == event_id).count()
    if count >= event.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Встреча уже заполнена",
        )

    participant = Participant(event_id=event_id, user_id=current_user.id)
    db.add(participant)

    db.query(User).filter(User.id == current_user.id).update(
        {User.meetings_count: func.coalesce(User.meetings_count, 0) + 1},
        synchronize_session=False,
    )

    db.commit()

    return {"status": "joined", "event_id": event_id}


@router.post("/{event_id}/leave", status_code=status.HTTP_200_OK)
def leave_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    participant = db.query(Participant).filter(
        Participant.event_id == event_id,
        Participant.user_id == current_user.id,
    ).first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ты не участник этой встречи",
        )

    db.delete(participant)

    db.query(User).filter(User.id == current_user.id).update(
        {User.meetings_count: func.greatest(func.coalesce(User.meetings_count, 0) - 1, 0)},
        synchronize_session=False,
    )

    db.commit()

    return {"status": "left", "event_id": event_id}
