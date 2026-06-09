from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class StudentProfileCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None

class StudentProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True

class UserCreateInitial(BaseModel):
    email: str
    password: str


# obsługa kursów ------------------------------------------

KategoriePrawaJazdy = Literal[
    "AM", "A1", "A2", "A",
    "B1", "B", "B+E",
    "C1", "C1+E", "C", "C+E",
    "D1", "D1+E", "D", "D+E", "T"
]

class CourseCreate(BaseModel):
    student_profile_id: UUID
    category: KategoriePrawaJazdy
    required_hours: Optional[int] = Field(default=30, ge=0)

class CoursePaymentUpdate(BaseModel):
    payment_status: Literal["PENDING", "PARTIALLY_PAID", "PAID", "REFUNDED"]

class CourseHoursUpdate(BaseModel):
    completed_hours: int = Field(..., ge=0, description="Total completed hours updated after a lesson")

class CourseResponse(BaseModel):
    id: UUID
    student_profile_id: UUID
    category: str
    required_hours: int
    completed_hours: int
    payment_status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True