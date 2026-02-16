from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Chat(BaseModel):
    chat_id: str
    client_id: str
    ip_address: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
