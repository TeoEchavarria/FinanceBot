from supabase import Client
from models.purchase import Purchase
from typing import Optional
from utils.serialization import serialize_model
from services.database_connection import get_supabase_client

def create_purchase(purchase: Purchase) -> Optional[Purchase]:
    client = get_supabase_client()
    purchase = serialize_model(purchase)
    response = client.table("purchases").insert(purchase).execute()

def get_purchases_by_user(user_id: str):
    client = get_supabase_client()
    response = client.table("purchases").select("*").eq("user_id", user_id).execute()
    return [Purchase(**item) for item in response.data]

def get_last_transactions_by_pocket(pocket_id: str):
    client = get_supabase_client()
    response = client.table("purchases").select("*").eq("pocket_id", pocket_id).order("created_at").limit(5).execute()
    return [Purchase(**item) for item in response.data]