from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime

class Pocket(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    balance: Decimal = Field(default_factory=lambda: Decimal('0.00'))
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
