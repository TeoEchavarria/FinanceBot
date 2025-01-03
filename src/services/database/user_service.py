from typing import Optional

def get_user_by_telegram_username(client, telegram_username: str) -> Optional[dict]:
    """
    Aquí interactúas directamente con la base de datos (Supabase, Mongo, etc.)
    Devuelve un diccionario con datos del usuario o None si no existe.
    """
    response = client.table("users").select("*").eq("username", telegram_username).single().execute()
    return response.data