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
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True