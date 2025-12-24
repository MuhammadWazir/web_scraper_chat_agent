from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional


class VoiceAgentRequest(BaseModel):
    website_url: HttpUrl
    target_audience: str
    company_name: str


class VoiceAgentResponse(BaseModel):
    client_id: str
    url: str