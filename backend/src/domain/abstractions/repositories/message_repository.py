from abc import ABC, abstractmethod
from typing import List, Dict
from src.domain.entities.message import Message


class IMessageRepository(ABC):
    @abstractmethod
    def create(self, message: Message) -> Message:
        pass
    
    @abstractmethod
    def get_by_id(self, message_id: str) -> Message:
        pass
    
    @abstractmethod
    def get_by_chat_id(self, chat_id: str) -> List[Message]:
        pass
    
    @abstractmethod
    def get_chat_history(self, chat_id: str, limit: int = 20) -> List[Dict[str, str]]:
        pass
    
    @abstractmethod
    def delete_by_chat_id(self, chat_id: str) -> bool:
        pass
