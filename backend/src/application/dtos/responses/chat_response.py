from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatResponse(BaseModel):
    chat_id: str
    client_id: str
    title: Optional[str] = None
    created_at: Optional[datetime] = None
