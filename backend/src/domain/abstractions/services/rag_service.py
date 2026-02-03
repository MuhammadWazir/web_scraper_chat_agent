from abc import ABC, abstractmethod
from typing import List, Dict, AsyncIterator, Optional


class IRAGService(ABC):
    @abstractmethod
    async def build(self, url: str, company_name: str) -> None:
        pass
    
    @abstractmethod
    async def query(self, question: str, company_name: str, chat_history: List[Dict[str, str]] = None) -> str:
        pass
    
    @abstractmethod
    async def query_stream(self, question: str, company_name: str, chat_history: List[Dict[str, str]] = None, tools: Optional[List[Dict]] = None, auth_token: Optional[str] = None, system_prompt: Optional[str] = "") -> AsyncIterator[str]:
        pass
