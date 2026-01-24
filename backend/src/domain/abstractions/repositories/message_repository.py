"""Message repository interface - defines the contract"""
from abc import ABC, abstractmethod
from typing import List, Literal
from src.domain.entities.message import Message


class IMessageRepository(ABC):
    """Repository interface for Message aggregate"""
    
    @abstractmethod
    def create(self, message: Message) -> Message:
        """Create a new message"""
        pass
    
    @abstractmethod
    def get_by_id(self, message_id: str) -> Message:
        """Get message by ID"""
        pass
    
    @abstractmethod
    def get_by_chat_id(self, chat_id: str) -> List[Message]:
        """Get all messages for a chat"""
        pass
    
    @abstractmethod
    def delete_by_chat_id(self, chat_id: str) -> bool:
        """Delete all messages for a chat"""
        pass
