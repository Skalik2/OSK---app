from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# Input to create the core Admin login row via Auth Microservice
class AdminAuthCreate(BaseModel):
    email: EmailStr
    password: str

# Input to populate the profile data row locally
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