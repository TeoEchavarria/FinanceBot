from supabase import Client
from models.pocket import Pocket
from typing import Optional
from utils.serialization import serialize_model
from services.database_connection import get_supabase_client

def create_pocket_service(pocket: Pocket) -> Optional[Pocket]:
    client = get_supabase_client()
    pocket = serialize_model(pocket)
    response = client.table("pockets").insert(pocket).execute()
    return Pocket(**response.data[0])

def get_pockets_by_user(user_id: str):
    client = get_supabase_client()
    response = client.table("pockets").select("*").eq("user_id", user_id).execute()
    if response.data != []:
        return [Pocket(**item) for item in response.data]
    return [create_pocket_service(Pocket(user_id=user_id, name="Default"))]

def get_pocket_by_user_and_name(user_id: str, pocket_name: str):
    client = get_supabase_client()
    response = client.table("pockets").select("*").eq("user_id", user_id).eq("name", pocket_name).execute()
    if response.data != []:
        return Pocket(**response.data[0])
    return None

def update_pocket_balance(pocket_id: str, amount: float):
    client = get_supabase_client()
    response = client.table("pockets").update({"balance": float(amount)}).eq("id", pocket_id).execute()
    return Pocket(**response.data[0])