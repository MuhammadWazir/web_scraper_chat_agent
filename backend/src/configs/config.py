import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
	"""Application settings loaded from environment variables."""
	agent_id: str
	database_url: str
	qdrant_api_key: str
	qdrant_cluster_endpoint: str


def load_settings() -> Settings:
	"""Load and validate application settings from environment variables."""
	openai_api_key = os.getenv("OPENAI_API_KEY", "")
	database_url = os.getenv("DATABASE_URL", "")
	qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
	qdrant_cluster_endpoint = os.getenv("QDRANT_CLUSTER_ENDPOINT", "")
	return Settings(
		openai_api_key=openai_api_key,
		database_url=database_url,
		qdrant_api_key=qdrant_api_key,
		qdrant_cluster_endpoint=qdrant_cluster_endpoint,
	)