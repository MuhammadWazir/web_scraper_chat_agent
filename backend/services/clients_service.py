import uuid
import time
import asyncio
from helpers.scrape import scrape_website
from helpers.ai_processor import process_prompts
from helpers.url_utils import generate_url_slug
from repositories.clients_repository import (
	add_client, 
	load_all_clients, 
	get_client_by_id, 
	get_client_by_url_slug, 
	update_client_prompts,
	update_client_voice
)
from services.websocket_manager import manager


async def create_chat_agent_service(website_url: str, target_audience: str, company_name: str) -> dict:
	...



