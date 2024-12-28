from supabase import Client
from models.purchase import Purchase
from typing import Optional

def create_purchase(client: Client, purchase: Purchase) -> Optional[Purchase]:
    response = client.table("purchases").insert(purchase.dict()).execute()
    if response.status_code == 201:
        return Purchase(**response.data[0])
    return None

def get_purchases_by_user(client: Client, user_id: str):
    response = client.table("purchases").select("*").eq("user_id", user_id).execute()
    if response.status_code == 200:
        return [Purchase(**item) for item in response.data]
    return []
