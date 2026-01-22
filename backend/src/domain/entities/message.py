"""Message domain entity - pure business logic"""
from datetime import datetime
from dataclasses import dataclass
from typing import Literal


@dataclass
class Message:
    """Message domain entity representing a chat message"""
    message_id: str
    chat_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    
    def __post_init__(self):
        """Validate entity invariants"""
        if not self.chat_id or not self.chat_id.strip():
            raise ValueError("Chat ID cannot be empty")
        if self.role not in ("user", "assistant"):
            raise ValueError("Role must be either 'user' or 'assistant'")
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")
