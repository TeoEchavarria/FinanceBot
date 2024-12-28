from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime

class Purchase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    pocket_id: UUID
    amount: Decimal
    description: str
    date: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True