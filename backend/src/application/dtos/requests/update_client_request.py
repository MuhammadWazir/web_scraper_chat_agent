from pydantic import BaseModel
from typing import Optional, List, Dict


class UpdateClientRequest(BaseModel):
    tools: Optional[List[Dict]] = None
