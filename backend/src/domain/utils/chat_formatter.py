"""Chat formatting utilities"""
from typing import List, Tuple, Dict, Any

def format_chat_history(chat_history: List[Dict[str, str]]) -> str:
    """format chat history as a conversation string"""
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

def format_chat_history_tuples(chat_history: List[Tuple[str, str]]) -> str:
    """Format chat history tuples as a conversation string"""
    if not chat_history:
        return ""
    
    formatted = "\n\nPrevious conversation:\n"
    for user_msg, ai_msg in chat_history:
        formatted += f"User: {user_msg}\n"
        formatted += f"Assistant: {ai_msg}\n"
    return formatted
