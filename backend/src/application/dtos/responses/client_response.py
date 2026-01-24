from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClientResponse(BaseModel):
    client_ip: str
    company_name: str
    website_url: str
    api_key: Optional[str] = None
    created_at: Optional[datetime] = None
