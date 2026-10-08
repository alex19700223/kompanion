from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional


# ========== AUTH ==========

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=2, max_length=100)
    birth_date: date
    ui_language: str = Field(default="de", max_length=5)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ========== USER ==========

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    birth_date: date
    age_verified: bool
    age_group: str
    city: Optional[str] = None
    avatar_id: Optional[str] = None
    bio: Optional[str] = None
    languages: list = []
    interests: list = []
    preferences: dict = {}
    ui_language: str = "de"

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    city: Optional[str] = Field(default=None, max_length=100)
    avatar_id: Optional[str] = Field(default=None, max_length=50)
    bio: Optional[str] = Field(default=None, max_length=300)
    languages: Optional[list] = None
    interests: Optional[list] = None
    preferences: Optional[dict] = None
    ui_language: Optional[str] = Field(default=None, max_length=5)


class UserPublicResponse(BaseModel):
    id: int
    name: str
    age_group: str
    city: Optional[str] = None
    avatar_id: Optional[str] = None
    bio: Optional[str] = None
    languages: list = []
    interests: list = []
    rating_avg: float = 0
    rating_count: int = 0
    meetings_count: int = 0

    class Config:
        from_attributes = True


# ========== VENUE ==========

class VenueCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    address: Optional[str] = Field(default=None, max_length=300)
    lat: Optional[float] = None
    lng: Optional[float] = None
    type: Optional[str] = Field(default=None, max_length=30)


class VenueResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    type: Optional[str] = None
    status: str
    is_promoted: bool

    class Config:
        from_attributes = True


# ========== EVENT ==========

class UserBrief(BaseModel):
    id: int
    name: str
    age_group: str

    class Config:
        from_attributes = True


class VenueBrief(BaseModel):
    id: int
    name: str
    address: Optional[str] = None

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    format: str = Field(max_length=30)
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    starts_at: datetime
    max_participants: int = Field(default=5, ge=2, le=20)
    venue_id: Optional[int] = None
    languages: list = []
    topics: list = []
    alcohol: bool = True


class EventResponse(BaseModel):
    id: int
    creator_id: int
    venue_id: Optional[int] = None
    format: str
    title: Optional[str] = None
    description: Optional[str] = None
    starts_at: datetime
    max_participants: int
    languages: list = []
    topics: list = []
    alcohol: bool
    status: str
    created_at: datetime

    creator: Optional[UserBrief] = None
    venue: Optional[VenueBrief] = None
    participants: list[UserBrief] = []
    participants_count: int = 0
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True
