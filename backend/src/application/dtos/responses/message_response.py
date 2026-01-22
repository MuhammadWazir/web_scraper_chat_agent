"""Response DTO for message data"""
from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class MessageResponse(BaseModel):
    """Response model for message data"""
    message_id: str
    chat_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True
