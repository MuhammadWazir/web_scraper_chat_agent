"""Request DTO for creating a client"""
from pydantic import BaseModel


class CreateClientRequest(BaseModel):
    """Request model for creating a client"""
    company_name: str
    website_url: str
