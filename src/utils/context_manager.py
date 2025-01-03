# En utils/context_manager.py
user_contexts = {}  # dict {telegram_user_id: context_data}

def set_user_context(user_id, key, value):
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    user_contexts[user_id][key] = value

def get_user_context(user_id, key):
    if user_id in user_contexts:
        return user_contexts[user_id].get(key)
    return None