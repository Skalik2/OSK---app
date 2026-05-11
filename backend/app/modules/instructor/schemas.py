from pydantic import BaseModel
from typing import Optional

class InstructorProfileCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None