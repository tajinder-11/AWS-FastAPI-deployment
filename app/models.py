from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)