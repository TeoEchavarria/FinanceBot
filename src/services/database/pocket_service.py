from supabase import Client
from models.pocket import Pocket
from typing import Optional
from utils.serialization import serialize_model

def create_pocket(client: Client, pocket: Pocket) -> Optional[Pocket]:
    pocket = serialize_model(pocket)
    response = client.table("pockets").insert(pocket).execute()
    return Pocket(**response.data[0])

def get_pockets_by_user(client: Client, user_id: str):
    response = client.table("pockets").select("*").eq("user_id", user_id).execute()
    if response.data != []:
        return [Pocket(**item) for item in response.data]
    return [create_pocket(client, Pocket(user_id=user_id, name="Default"))]
