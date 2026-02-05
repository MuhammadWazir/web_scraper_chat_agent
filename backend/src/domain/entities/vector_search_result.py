from pydantic import BaseModel
from typing import Optional, Dict, Any


class VectorSearchResult(BaseModel):
    text: str
    score: float
    chunk_index: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
