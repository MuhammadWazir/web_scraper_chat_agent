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


async def create_voice_agent_service(website_url: str, target_audience: str, company_name: str) -> dict:
	request_data = {
		"website_url": str(website_url),
		"target_audience": target_audience,
	}

	url_slug = generate_url_slug(company_name)

	# Save client immediately with null prompts
	null_prompts = {
		"background": None,
		"rules": None,
		"script": None,
		"faqs": None,
	}
	client_id = add_client(request_data, null_prompts, company_name)
	if not client_id:
		raise Exception("Failed to create client")

	# Process prompts in background
	asyncio.create_task(process_prompts_background(client_id, website_url, target_audience))

	return {
		"client_id": client_id,
		"url_slug": url_slug,
	}


async def process_prompts_background(client_id: str, website_url: str, target_audience: str):
	try:
		website_content = await scrape_website(str(website_url))
		assets = await process_prompts(
			str(website_url),
			website_content,
			target_audience,
			"gpt-5",
		)

		update_success = update_client_prompts(client_id, assets)
		if update_success:
			updated_client = get_client_by_id(client_id)
			if updated_client:
				updated_client = _add_url_slug_to_client(updated_client)
				await manager.broadcast_client_update(updated_client)
	except Exception as e:
		pass


def _add_url_slug_to_client(client: dict) -> dict:
	if client and client.get('company_name'):
		client['url_slug'] = generate_url_slug(client['company_name'])
	return client


def get_all_clients_service() -> list[dict]:
	clients = load_all_clients()
	return [_add_url_slug_to_client(client) for client in clients]


def get_client_by_id_service(client_id: str) -> dict | None:
	client = get_client_by_id(client_id)
	return _add_url_slug_to_client(client) if client else None


def get_client_by_url_slug_service(url_slug: str) -> dict | None:
	client = get_client_by_url_slug(url_slug)
	return _add_url_slug_to_client(client) if client else None


def get_client_voice_service(url_slug: str) -> str | None:
	client = get_client_by_url_slug(url_slug)
	if not client:
		return None
	return client.get('voice_id')


def update_client_voice_service(url_slug: str, voice_id: str | None) -> bool:
	client = get_client_by_url_slug(url_slug)
	if not client:
		return False
	return update_client_voice(client.get('client_id'), voice_id)


