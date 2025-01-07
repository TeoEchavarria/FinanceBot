from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    created_at: datetime = Field(default_factory=datetime.now)
    audio_time: float = 90
    membresia: Literal["free", "pro"] = "free"

    class Config:
        # Desde Pydantic v2, 'orm_mode' se reemplaza por 'from_attributes'
        from_attributes = True
