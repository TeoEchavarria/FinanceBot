from typing import Optional
from services.database_connection import get_supabase_client

def get_user_by_telegram_username(telegram_username: str) -> Optional[dict]:
    """
    Aquí interactúas directamente con la base de datos (Supabase, Mongo, etc.)
    Devuelve un diccionario con datos del usuario o None si no existe.
    """
    client = get_supabase_client()
    response = client.table("users").select("*").eq("username", telegram_username).single().execute()
    return response.data