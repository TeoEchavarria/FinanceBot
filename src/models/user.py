from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4
from datetime import datetime

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now())

    class Config:
        orm_mode = True