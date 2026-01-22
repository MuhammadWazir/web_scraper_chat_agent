"""RAG service interface - defines the contract for RAG operations"""
from abc import ABC, abstractmethod
from typing import List, Dict


class IRAGService(ABC):
    """Service interface for RAG (Retrieval-Augmented Generation) operations"""
    
    @abstractmethod
    async def build(self, url: str, company_name: str) -> None:
        """Build and persist the vector store for a company URL"""
        pass
    
    @abstractmethod
    async def query(self, question: str, company_name: str, chat_history: List[Dict[str, str]] = None) -> str:
        """Query the RAG system with a question and optional chat history"""
        pass
