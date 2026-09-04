from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from rejesha_green.models.activity import UserGroup


class ActivityCreate(BaseModel):
    created_by: UUID
    zone_id: UUID
    activity_name: str = Field(..., max_length=100)
    scheduled_date: datetime
    description: Optional[str] = None
    user_group: Optional[UserGroup] = None
    expected_attendees: int = Field(..., ge=0)
    actual_attendees: int = Field(default=0, ge=0)


class ActivityUpdate(BaseModel):
    zone_id: Optional[UUID] = None
    activity_name: Optional[str] = Field(None, max_length=100)
    scheduled_date: Optional[date] = None
    description: Optional[str] = None
    user_group: Optional[UserGroup] = None
    expected_attendees: Optional[int] = Field(None, ge=0)
    actual_attendees: Optional[int] = Field(None, ge=0)


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_id: UUID
    created_by: UUID
    zone_id: UUID
    activity_name: str
    scheduled_date: date
    description: Optional[str]
    user_group: Optional[UserGroup]
    expected_attendees: int
    actual_attendees: int
    created_at: datetime


