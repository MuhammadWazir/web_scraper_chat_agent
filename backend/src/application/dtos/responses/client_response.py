"""Response DTO for client data"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClientResponse(BaseModel):
    """Response model for client data"""
    client_id: str
    company_name: str
    website_url: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
