# --- PATH: app/modules/calendar/schemas.py ---
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class ProfileMinInfo(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    id: UUID
    instructor_profile_id: UUID = Field(..., alias="instructor_id")
    student_profile_id: UUID = Field(..., alias="student_id")
    start_time: datetime
    end_time: datetime
    status: str
    created_at: Optional[datetime]

    instructor: Optional[ProfileMinInfo] = None
    student: Optional[ProfileMinInfo] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class LessonCreate(BaseModel):
    instructor_profile_id: UUID
    student_profile_id: UUID
    start_time: datetime
    end_time: datetime
    status: Optional[str] = "SCHEDULED"


class LessonUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None