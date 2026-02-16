from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class Client(BaseModel):
    client_id: str
    client_ip: str
    client_name: str
    client_url: str
    api_key_hash: Optional[str]
    tools: Optional[List[Dict]] = None
    system_prompt: Optional[str] = None
    created_at: datetime
    updated_at: datetime