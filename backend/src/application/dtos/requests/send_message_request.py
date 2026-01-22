"""Request DTO for sending a message"""
from pydantic import BaseModel
from typing import Optional


class SendMessageRequest(BaseModel):
    """Request model for sending a message in a chat"""
    client_id: str
    chat_id: Optional[str] = None
    message: str
