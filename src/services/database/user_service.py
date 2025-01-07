from typing import Optional
from services.database_connection import get_supabase_client
from models.user import User
from utils.serialization import serialize_model

def get_user_by_telegram_username(telegram_username: str) -> Optional[dict]:
    """
    Aquí interactúas directamente con la base de datos (Supabase, Mongo, etc.)
    Devuelve un diccionario con datos del usuario o None si no existe.
    """
    client = get_supabase_client()
    response = client.table("users").select("*").eq("username", telegram_username).single().execute()
    return response.data

def create_user(user: User) -> Optional[dict]:
    """
    Aquí interactúas directamente con la base de datos (Supabase, Mongo, etc.)
    Crea un usuario en la base de datos y devuelve el usuario creado.
    """
    client = get_supabase_client()
    user = serialize_model(user)
    response = client.table("users").insert(user).execute()
    return response.data