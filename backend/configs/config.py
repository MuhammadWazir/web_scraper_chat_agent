import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from a local .env file if present
load_dotenv()


@dataclass(frozen=True)
class Settings:
	"""Application settings loaded from environment variables."""
	eleven_labs_ws_url: str
	openai_api_key: str
	xi_api_key: str
	agent_id: str


def load_settings() -> Settings:
	"""Load and validate application settings from environment variables."""
	openai_api_key = os.getenv("OPENAI_API_KEY", "")
	eleven_labs_ws_url = os.getenv("ELEVENLABS_WS_URL", "")
	xi_api_key = os.getenv("XI_API_KEY", "")
	agent_id = os.getenv("AGENT_ID", "")
	return Settings(
		openai_api_key=openai_api_key,
		eleven_labs_ws_url=eleven_labs_ws_url,
		xi_api_key=xi_api_key,
		agent_id=agent_id,
	)