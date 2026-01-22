"""Response DTO for chat data"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatResponse(BaseModel):
    """Response model for chat data"""
    chat_id: str
    client_id: str
    title: Optional[str] = None
    ip_address: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
