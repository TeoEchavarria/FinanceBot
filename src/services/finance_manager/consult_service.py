from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from services.database.pocket_service import get_pockets_by_user, get_pocket_by_user_and_name
from services.database.purchase_service import get_purchases_by_pocket

from utils.serialization import serialize_model

def query_finances(query_type: str,
                   pocket_name: Optional[str] = None,
                   amount: Optional[float] = None,
                   time_range: Optional[str] = None,
                   user_id: Optional[UUID] = None
                  ):
    # (Implementation of query_finances as provided by the user)
    start_date, end_date = None, None
    if time_range:
        if time_range == "last month":
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        elif time_range == "last 6 months":
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
        elif time_range == "all time":
            pass

    result = {}

    if query_type == "list_pockets":
        pockets = get_pockets_by_user(user_id)
        result["pockets"] = [serialize_model(p) for p in pockets]

    elif query_type == "pocket_balance":
        if not pocket_name:
            return {"error": "pocket_name is required for pocket_balance query"}
        pocket = get_pocket_by_user_and_name(user_id, pocket_name)
        if not pocket:
            return {"error": f"No pocket found with name '{pocket_name}'"}
        result["balance"] = str(pocket.balance)

    elif query_type == "pocket_expenses":
        if not pocket_name:
            return {"error": "pocket_name is required for pocket_expenses query"}
        pocket = get_pocket_by_user_and_name(user_id, pocket_name)
        if not pocket:
            return {"error": f"No pocket found with name '{pocket_name}'"}
        purchases = get_purchases_by_pocket(pocket.id, start_date, end_date)
        total_expenses = sum(p.amount for p in purchases)
        result["total_expenses"] = str(total_expenses)

    elif query_type == "compare_balance":
        if not pocket_name or amount is None:
            return {"error": "pocket_name and amount are required for compare_balance query"}
        pocket = get_pocket_by_user_and_name(user_id, pocket_name)
        if not pocket:
            return {"error": f"No pocket found with name '{pocket_name}'"}
        pocket_balance = pocket.balance
        comparison_amount = float(amount)
        can_afford = (pocket_balance >= comparison_amount)
        result["pocket_balance"] = str(pocket_balance)
        result["comparison_amount"] = str(comparison_amount)
        result["can_afford"] = can_afford

    elif query_type == "sum_purchases":
        if pocket_name:
            pocket = get_pocket_by_user_and_name(user_id, pocket_name)
            if not pocket:
                return {"error": f"No pocket found with name '{pocket_name}'"}
            purchases = get_purchases_by_pocket(pocket.id, start_date, end_date)
        else:
            pockets = get_pockets_by_user(user_id)
            purchases = []
            for pck in pockets:
                purchases.extend(get_purchases_by_pocket(pck.id, start_date, end_date))
        total = sum(p.amount for p in purchases)
        result["total_purchases"] = str(total)

    elif query_type == "average_purchase_amount":
        if pocket_name:
            pocket = get_pocket_by_user_and_name(user_id, pocket_name)
            if not pocket:
                return {"error": f"No pocket found with name '{pocket_name}'"}
            purchases = get_purchases_by_pocket(pocket.id, start_date, end_date)
        else:
            pockets = get_pockets_by_user(user_id)
            purchases = []
            for pck in pockets:
                purchases.extend(get_purchases_by_pocket(pck.id, start_date, end_date))
        if not purchases:
            result["average_purchase_amount"] = "0"
        else:
            avg = sum(p.amount for p in purchases) / len(purchases)
            result["average_purchase_amount"] = str(avg)

    else:
        result["error"] = f"Unknown query_type: {query_type}"

    return result
