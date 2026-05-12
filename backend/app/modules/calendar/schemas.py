from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ProfileMinInfo(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    phone: Optional[str] = None


class LessonResponse(BaseModel):
    id: UUID
    instructor_id: UUID
    student_id: UUID
    start_time: datetime
    end_time: datetime
    status: str
    created_at: Optional[datetime]

    # Include both, so any view (Admin/Student/Instructor) has the full context
    instructor: Optional[ProfileMinInfo] = None
    student: Optional[ProfileMinInfo] = None

class Config:
    from_attributes = True

class LessonCreate(BaseModel):
    instructor_id: UUID
    student_id: UUID
    start_time: datetime
    end_time: datetime
    status: Optional[str] = "SCHEDULED"
    
class LessonUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None