from pydantic import BaseModel


class CreateChatDTO(BaseModel):
    client_id: str
    title: str | None = None

