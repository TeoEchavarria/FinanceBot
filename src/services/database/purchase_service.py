from supabase import Client
from models.purchase import Purchase
from typing import Optional
from utils.serialization import serialize_model

def create_purchase(client: Client, purchase: Purchase) -> Optional[Purchase]:
    purchase = serialize_model(purchase)
    response = client.table("purchases").insert(purchase).execute()

def get_purchases_by_user(client: Client, user_id: str):
    response = client.table("purchases").select("*").eq("user_id", user_id).execute()
    return [Purchase(**item) for item in response.data]
