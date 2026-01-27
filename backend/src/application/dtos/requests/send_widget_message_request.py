from pydantic import BaseModel
from typing import Optional

class SendWidgetMessageRequest(BaseModel):
    content: str
    authorization: Optional[str] = None
