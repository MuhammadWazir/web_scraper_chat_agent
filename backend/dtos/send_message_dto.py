from pydantic import BaseModel
from typing import Optional


class SendMessageDTO(BaseModel):
    chat_id: Optional[str] = None
    client_id: str
    message: str

