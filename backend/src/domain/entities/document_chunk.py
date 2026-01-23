from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class DocumentChunk(BaseModel):
    text: str
    embedding: List[float]
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = None
    

