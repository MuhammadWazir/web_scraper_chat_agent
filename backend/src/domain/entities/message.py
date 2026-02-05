from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
    message_id: str
    chat_id: str
    content: str
    ai_generated: bool
    created_at: datetime
    updated_at: datetime
