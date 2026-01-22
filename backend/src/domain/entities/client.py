"""Client domain entity - pure business logic"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Client:
    """Client domain entity representing a business client"""
    client_id: str
    client_name: str
    client_url: str
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        """Validate entity invariants"""
        if not self.client_name or not self.client_name.strip():
            raise ValueError("Client name cannot be empty")
        if not self.client_url or not self.client_url.strip():
            raise ValueError("Client URL cannot be empty")
        if not self.client_url.startswith(('http://', 'https://')):
            raise ValueError("Client URL must be a valid HTTP(S) URL")
    
    def update_info(self, client_name: Optional[str] = None, client_url: Optional[str] = None):
        """Update client information"""
        if client_name is not None:
            if not client_name.strip():
                raise ValueError("Client name cannot be empty")
            self.client_name = client_name
        
        if client_url is not None:
            if not client_url.strip():
                raise ValueError("Client URL cannot be empty")
            if not client_url.startswith(('http://', 'https://')):
                raise ValueError("Client URL must be a valid HTTP(S) URL")
            self.client_url = client_url
        
        self.updated_at = datetime.utcnow()
