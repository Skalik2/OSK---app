from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

class UserOut(BaseModel):
    # Changed from int to UUID to match your SQLAlchemy Mapped[uuid.UUID]
    id: UUID
    email: EmailStr
    # You can add 'role' here if you want it returned to the frontend
    role: str

    # In Pydantic v2, we use model_config instead of class Config
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None