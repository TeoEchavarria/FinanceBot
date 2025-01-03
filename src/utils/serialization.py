from typing import Any, Dict
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

def serialize_model(model: BaseModel) -> Dict[str, Any]:
    """
    Convierte un modelo Pydantic a un diccionario con tipos JSON serializables.
    """
    data = model.model_dump()
    serialized_data = {}
    for key, value in data.items():
        if isinstance(value, UUID):
            serialized_data[key] = str(value)
        elif isinstance(value, Decimal):
            serialized_data[key] = float(value)  # O str(value) si prefieres
        elif isinstance(value, datetime):
            serialized_data[key] = value.isoformat()
        else:
            serialized_data[key] = value
    return serialized_data