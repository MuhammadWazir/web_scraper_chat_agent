from pydantic import BaseModel

class SendWidgetMessageRequest(BaseModel):
    content: str
