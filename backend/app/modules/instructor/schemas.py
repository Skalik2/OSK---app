from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class InstructorProfileCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None

class InstructorProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True

class SpecialtyCreate(BaseModel):
    category: str

class SpecialtyResponse(BaseModel):
    id: UUID
    category: str
    instructor_profile_id: UUID

    class Config:
        from_attributes = True