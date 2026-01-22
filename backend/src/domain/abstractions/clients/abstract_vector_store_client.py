"""Abstract base class for vector store clients"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from src.domain.entities.vector_search_result import VectorSearchResult


class AbstractVectorStoreClient(ABC):
    """Abstract interface for vector store operations"""

    @abstractmethod
    def ensure_collection(
        self, 
        collection_name: str, 
        vector_size: int = 1536, 
        distance: str = "Cosine"
    ) -> None:
        """Ensure a collection exists, create if it doesn't"""
        pass

    @abstractmethod
    def upload(
        self,
        collection_name: str,
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None,
        vector_size: Optional[int] = None
    ) -> str:
        """Upload embeddings with metadata to a collection"""
        pass

    @abstractmethod
    def search_chunks(
        self,
        collection_name: str,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[VectorSearchResult]:
        """Search for similar chunks in a collection"""
        pass

    @abstractmethod
    def search_all_collections(
        self,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[VectorSearchResult]:
        """Search across all collections"""
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> Dict:
        """Delete a collection"""
        pass

    @abstractmethod
    def list_collections(self) -> List[str]:
        """List all available collections"""
        pass
