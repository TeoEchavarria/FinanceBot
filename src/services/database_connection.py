from supabase import create_client, Client
import os

def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Las variables de entorno SUPABASE_URL y SUPABASE_KEY deben estar configuradas.")
    return create_client(url, key)