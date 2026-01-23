"""Widget session repository interface"""
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.widget_session import WidgetSession


class IWidgetSessionRepository(ABC):
    """Interface for widget session repository"""
    
    @abstractmethod
    def create(self, widget_session: WidgetSession) -> WidgetSession:
        """Create a new widget session"""
        pass
    
    @abstractmethod
    def get_by_token(self, session_token: str) -> Optional[WidgetSession]:
        """Get widget session by token"""
        pass
    
    @abstractmethod
    def update(self, widget_session: WidgetSession) -> WidgetSession:
        """Update widget session (e.g., bind to IP address)"""
        pass
    
    @abstractmethod
    def delete_expired(self) -> int:
        """Delete all expired sessions, returns count of deleted sessions"""
        pass
