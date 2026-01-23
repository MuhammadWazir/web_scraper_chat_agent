"""Widget session domain entity - pure business logic"""
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass
import uuid


@dataclass
class WidgetSession:
    """Widget session entity for one-time widget initialization"""
    session_token: str
    client_id: str
    end_user_ip: Optional[str]
    expires_at: datetime
    created_at: datetime
    
    @staticmethod
    def create_new(client_id: str, validity_hours: int = 24) -> 'WidgetSession':
        """Create a new widget session with auto-generated token"""
        now = datetime.utcnow()
        return WidgetSession(
            session_token=str(uuid.uuid4()),
            client_id=client_id,
            end_user_ip=None,
            expires_at=now + timedelta(hours=validity_hours),
            created_at=now
        )
    
    def is_expired(self) -> bool:
        """Check if the session token has expired"""
        return datetime.utcnow() > self.expires_at
    
    def bind_to_user(self, ip_address: str) -> None:
        """Bind this session to an end-user's IP address"""
        if self.end_user_ip is not None:
            raise ValueError("Session already bound to an IP address")
        if self.is_expired():
            raise ValueError("Cannot bind expired session")
        self.end_user_ip = ip_address
    
    def validate(self, ip_address: str) -> bool:
        """Validate that the session belongs to the given IP address"""
        if self.is_expired():
            return False
        if self.end_user_ip is None:
            return False
        return self.end_user_ip == ip_address
