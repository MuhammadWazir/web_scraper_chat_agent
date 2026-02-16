from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ClientResponse(BaseModel):
    client_id: str
    client_ip: str
    company_name: str
    website_url: str
    api_key: Optional[str] = None
    tools: Optional[List[dict]] = None
    system_prompt: Optional[str] = None
    created_at: Optional[datetime] = None
