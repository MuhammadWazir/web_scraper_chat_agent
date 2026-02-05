from pydantic import BaseModel
from typing import Optional

class SendWidgetMessageRequest(BaseModel):
    content: str
    authorization: Optional[str] = None
    is_follow_up: bool = False
