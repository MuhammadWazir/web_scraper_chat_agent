"""Abstract base class for web crawling clients"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain.schema import Document


class AbstractCrawlingClient(ABC):
    """Abstract interface for web crawling operations"""

    @abstractmethod
    async def scrape_website(self, url: str) -> List[Document]:
        """Scrape content from a single URL"""
        pass
