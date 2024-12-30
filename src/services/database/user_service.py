from supabase import Client
from models.user import User
from typing import Optional

def get_user_by_email(client: Client, email: str) -> Optional[User]:
    response = client.table("users").select("*").eq("email", email).single().execute()
    if response.status_code == 200 and response.data:
        return User(**response.data)
    return None
