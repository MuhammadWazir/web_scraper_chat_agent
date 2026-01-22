"""Domain entity for vector search results"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class VectorSearchResult:
    """Represents a single vector search result"""
    text: str
    score: float
    chunk_index: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Ensure metadata is a dict"""
        if self.metadata is None:
            self.metadata = {}
