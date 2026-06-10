from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class AdminAuthCreate(BaseModel):
    email: EmailStr
    password: str

class AdminProfileCreate(BaseModel):
    user_id: UUID
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    position: Optional[str] = Field(None, max_length=100)

class AdminPositionUpdate(BaseModel):
    position: Optional[str] = Field(None, max_length=100)

class AdminProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    position: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True



class UserMinResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class InstructorAdminResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    phone: Optional[str]
    license_number: Optional[str]
    bio: Optional[str]
    created_at: Optional[datetime]
    user: UserMinResponse  # Pulls the linked auth user information

    class Config:
        from_attributes = True


class StudentMinAdminResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    phone: Optional[str]

    class Config:
        from_attributes = True


class CourseAdminResponse(BaseModel):
    id: UUID
    student_profile_id: UUID
    category: str
    required_hours: int
    completed_hours: int
    payment_status: str
    created_at: Optional[datetime]

    student_profile: Optional[StudentMinAdminResponse] = None

    class Config:
        from_attributes = True


class StudentAdminResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    phone: Optional[str]
    user: UserMinResponse  # Pulls the linked auth user information

    class Config:
        from_attributes = True