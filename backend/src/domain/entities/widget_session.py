from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class WidgetSession(BaseModel):
    session_token: str
    client_id: str
    end_user_ip: Optional[str] = None
    expires_at: datetime
    created_at: datetime
