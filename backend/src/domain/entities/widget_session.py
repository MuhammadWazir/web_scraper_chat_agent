from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class WidgetSession(BaseModel):
    session_token: str
    client_ip: str
    end_user_ip: Optional[str]
    expires_at: datetime
    created_at: datetime
