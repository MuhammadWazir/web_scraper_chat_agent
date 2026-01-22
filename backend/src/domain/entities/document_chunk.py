"""Domain entity for document chunks"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class DocumentChunk:
    """Represents a document chunk for vector storage"""
    text: str
    embedding: List[float]
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Ensure metadata is a dict"""
        if self.metadata is None:
            self.metadata = {}
