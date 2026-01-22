"""Chat domain entity - pure business logic"""
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class Chat:
    """Chat domain entity representing a conversation"""
    chat_id: str
    client_id: str
    title: Optional[str]
    ip_address: str
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        """Validate entity invariants"""
        if not self.client_id or not self.client_id.strip():
            raise ValueError("Client ID cannot be empty")
        if not self.ip_address or not self.ip_address.strip():
            raise ValueError("IP address cannot be empty")
    
    def update_title(self, title: str):
        """Update chat title"""
        if title and title.strip():
            self.title = title
            self.updated_at = datetime.utcnow()
