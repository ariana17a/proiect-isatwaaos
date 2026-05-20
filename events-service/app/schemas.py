from datetime import date as dt_date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

UserRole = Literal["student", "organizer", "admin"]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int
    role: UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = "student"


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EventBase(BaseModel):
    title: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime
    location: str
    category: str
    participation_type: Literal["onsite", "online", "hybrid"]
    organizer: str
    registration_link: str | None = None


class EventCreate(EventBase):
    is_published: bool = False


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    location: str | None = None
    category: str | None = None
    participation_type: Literal["onsite", "online", "hybrid"] | None = None
    organizer: str | None = None
    registration_link: str | None = None
    qr_code_url: str | None = None
    is_published: bool | None = None


class EventOut(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    qr_code_url: str | None = None
    is_published: bool
    created_by: int


class EventResponse(EventOut):
    pass


class EventFilters(BaseModel):
    category: str | None = None
    location: str | None = None
    organizer: str | None = None
    date: dt_date | None = None
    participation_type: Literal["onsite", "online", "hybrid"] | None = None


class FeedbackBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class FeedbackCreate(FeedbackBase):
    event_id: int


class FeedbackOut(FeedbackBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    user_id: int
    created_at: datetime


class FeedbackStats(BaseModel):
    event_id: int
    total_reviews: int
    average_rating: float
    rating_breakdown: dict[int, int]  # {1: count, 2: count, ..., 5: count}
