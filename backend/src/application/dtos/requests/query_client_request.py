"""Request DTO for querying a client (legacy)"""
from pydantic import BaseModel


class QueryClientRequest(BaseModel):
    """Request model for querying a client (deprecated)"""
    query: str
    client_id: str
