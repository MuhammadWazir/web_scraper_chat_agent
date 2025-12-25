from pydantic import BaseModel


class SendMessageDTO(BaseModel):
    chat_id: str
    message: str

