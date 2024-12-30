from typing import Optional
from services.database_connection import get_supabase_client
from typing import Optional

def get_user_by_telegram_username(telegram_username: str) -> Optional[dict]:
    """
    Aquí interactúas directamente con la base de datos (Supabase, Mongo, etc.)
    Devuelve un diccionario con datos del usuario o None si no existe.
    """
    client = get_supabase_client()
    response = client.table("users").select("*").eq("telegram_username", telegram_username).single().execute()
    if response.status_code == 200 and response.data:
        return response.data  # o un objeto de tu modelo de usuario
    return None