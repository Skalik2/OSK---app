from pydantic import BaseModel
from typing import Optional

class StudentProfileCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None