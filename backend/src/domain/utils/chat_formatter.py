from typing import List, Dict

def format_chat_history(chat_history: List[Dict[str, str]]) -> str:
    if not chat_history:
        return ""
    
    formatted = "\n\nPrevious conversation:\n"
    for message in chat_history:
        user_msg = message.get("user", "")
        ai_msg = message.get("assistant", "")
        if user_msg:
            formatted += f"User: {user_msg}\n"
        if ai_msg:
            formatted += f"Assistant: {ai_msg}\n"
    return formatted
