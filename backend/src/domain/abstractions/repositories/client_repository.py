"""Client repository interface - defines the contract"""
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.client import Client


class IClientRepository(ABC):
    """Repository interface for Client aggregate"""
    
    @abstractmethod
    def create(self, client_name: str, client_url: str) -> Client:
        """Create a new client"""
        pass
    
    @abstractmethod
    def get_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID"""
        pass
    
    @abstractmethod
    def get_by_name(self, client_name: str) -> Optional[Client]:
        """Get client by name"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[Client]:
        """Get all clients"""
        pass
    
    @abstractmethod
    def update(self, client: Client) -> Client:
        """Update a client"""
        pass
    
    @abstractmethod
    def delete(self, client_id: str) -> bool:
        """Delete a client"""
        pass
