from supabase import Client
from models.pocket import Pocket
from typing import Optional

def create_pocket(client: Client, pocket: Pocket) -> Optional[Pocket]:
    response = client.table("pockets").insert(pocket.dict()).execute()
    if response.status_code == 201:
        return Pocket(**response.data[0])
    return None

def get_pockets_by_user(client: Client, user_id: str):
    response = client.table("pockets").select("*").eq("user_id", user_id).execute()
    if response.status_code == 200:
        return [Pocket(**item) for item in response.data]
    return []
