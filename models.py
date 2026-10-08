from sqlalchemy import Column, BigInteger, String, Date, Boolean, Integer, Numeric, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(BigInteger, primary_key=True, index=True)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    password_hash   = Column(String(255), nullable=False)
    name            = Column(String(100), nullable=False)
    birth_date      = Column(Date, nullable=False)
    age_verified    = Column(Boolean, default=False)
    age_group       = Column(String(10), default="adult")
    ui_language     = Column(String(5), server_default="de")
    city            = Column(String(100))
    avatar_id       = Column(String(50))
    bio             = Column(String(300))
    languages       = Column(JSONB, server_default=text("'[]'::jsonb"))
    interests       = Column(JSONB, server_default=text("'[]'::jsonb"))
    preferences     = Column(JSONB, server_default=text("'{}'::jsonb"))
    rating_avg      = Column(Numeric(2, 1), default=0)
    rating_count    = Column(Integer, default=0)
    meetings_count  = Column(Integer, default=0)
    is_blocked      = Column(Boolean, default=False)
    created_at      = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    updated_at      = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))


class Venue(Base):
    __tablename__ = "venues"

    id          = Column(BigInteger, primary_key=True, index=True)
    name        = Column(String(200), nullable=False)
    address     = Column(String(300))
    lat         = Column(Numeric(10, 7))
    lng         = Column(Numeric(10, 7))
    type        = Column(String(30))
    status      = Column(String(20), server_default="user_suggested")
    is_promoted = Column(Boolean, server_default="false")
    created_by  = Column(BigInteger, ForeignKey("users.id"))
    created_at  = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))


class Event(Base):
    __tablename__ = "events"

    id                = Column(BigInteger, primary_key=True, index=True)
    creator_id        = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    venue_id          = Column(BigInteger, ForeignKey("venues.id"))
    format            = Column(String(30), nullable=False)
    title             = Column(String(200))
    description       = Column(String(500))
    starts_at         = Column(TIMESTAMP(timezone=True), nullable=False)
    max_participants  = Column(Integer, server_default="5")
    languages         = Column(JSONB, server_default=text("'[]'::jsonb"))
    topics            = Column(JSONB, server_default=text("'[]'::jsonb"))
    alcohol           = Column(Boolean, server_default="true")
    status            = Column(String(20), server_default="active")
    created_at        = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))


class Participant(Base):
    __tablename__ = "participants"

    id         = Column(BigInteger, primary_key=True, index=True)
    event_id   = Column(BigInteger, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status     = Column(String(20), server_default="joined")
    joined_at  = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
