"""Abstract base class for LLM clients"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncIterator, Any


class AbstractLLMClient(ABC):
    """Abstract interface for LLM operations"""

    @abstractmethod
    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """Create a chat completion"""
        pass

    @abstractmethod
    async def create_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Create a streaming chat completion"""
        pass

    @abstractmethod
    async def create_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Create an embedding for text"""
        pass

    @abstractmethod
    async def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        pass

    @abstractmethod
    async def summarize_chunks_in_parallel(
        self,
        chunks: List[str],
        model: Optional[str] = None
    ) -> str:
        pass
