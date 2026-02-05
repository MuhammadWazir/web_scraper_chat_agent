"""Chat repository interface - defines the contract"""
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.chat import Chat


class IChatRepository(ABC):
    """Repository interface for Chat aggregate"""
    
    @abstractmethod
    def create(self, client_id: str, ip_address: str, title: Optional[str] = None) -> Chat:
        """Create a new chat"""
        pass
    
    @abstractmethod
    def get_by_id(self, chat_id: str) -> Optional[Chat]:
        """Get chat by ID"""
        pass
    
    @abstractmethod
    def get_by_client_id(self, client_id: str) -> List[Chat]:
        """Get all chats for a client"""
        pass
    
    @abstractmethod
    def update(self, chat: Chat) -> Chat:
        """Update a chat"""
        pass
    
    @abstractmethod
    def delete(self, chat_id: str) -> bool:
        """Delete a chat"""
        pass
