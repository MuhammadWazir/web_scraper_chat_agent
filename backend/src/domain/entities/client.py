from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Client(BaseModel):
    client_ip: str
    client_name: str
    client_url: str
    api_key_hash: Optional[str]
    created_at: datetime
    updated_at: datetime