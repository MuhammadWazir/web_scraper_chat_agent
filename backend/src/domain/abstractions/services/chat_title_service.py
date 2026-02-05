"""Chat title service interface - defines the contract for generating chat titles"""
from abc import ABC, abstractmethod


class IChatTitleService(ABC):
    """Service interface for generating chat titles"""
    
    @abstractmethod
    async def generate_title(self, first_message: str) -> str:
        """Generate a chat title from the first message"""
        pass
