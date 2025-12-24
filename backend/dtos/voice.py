from pydantic import BaseModel
from typing import Optional


class VoiceUpdate(BaseModel):
	voice_id: Optional[str]
