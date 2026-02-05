"""Request DTO for creating a chat"""
from pydantic import BaseModel


class CreateChatRequest(BaseModel):
    """Request model for creating a chat"""
    client_id: str
