from pydantic import BaseModel
from typing import Optional, Dict

class OverallPromptData(BaseModel):
    overall_prompt: str

class OverallPromptResponse(OverallPromptData):
    is_custom: bool

