import json
import uuid
from typing import Any, Dict, List, Optional
from helpers.url_utils import generate_url_slug

DATA_FILE = 'data.json'


def load_all_clients() -> List[Dict[str, Any]]:
	try:
		with open(DATA_FILE, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return data.get('clients', [])
	except FileNotFoundError:
		return []


def save_all_clients(clients: List[Dict[str, Any]]) -> None:
	data = {"clients": clients}
	with open(DATA_FILE, 'w', encoding='utf-8') as f:
		json.dump(data, f, indent=4)


def get_client_by_id(client_id: str) -> Optional[Dict[str, Any]]:
	clients = load_all_clients()
	for client in clients:
		if client.get('client_id') == client_id:
			return client
	return None


def get_client_by_url_slug(url_slug: str) -> Optional[Dict[str, Any]]:
	clients = load_all_clients()
	for client in clients:
		company_name = client.get('company_name', '')
		if generate_url_slug(company_name) == url_slug:
			return client
	return None


def get_all_url_slugs() -> list[str]:
	clients = load_all_clients()
	return [generate_url_slug(client.get('company_name', '')) for client in clients if client.get('company_name')]


def add_client(request_data: Dict[str, Any], prompts: Dict[str, Any], company_name: str) -> str | None:
	try:
		clients = load_all_clients()
		client_id = str(uuid.uuid4())
		new_client = {
			"client_id": client_id,
			"request": request_data,
			"company_name": company_name,
			"prompts": prompts,
			"voice_id": None,
			"custom_overall_prompt": None,
		}
		clients.append(new_client)
		save_all_clients(clients)
		return client_id
	except Exception as e:
		print(f"Error saving client data: {e}")
		return None


def update_client_prompts(client_id: str, prompts: Dict[str, Any]) -> bool:
	try:
		clients = load_all_clients()
		for client in clients:
			if client.get('client_id') == client_id:
				client['prompts'] = prompts
				save_all_clients(clients)
				return True
		return False
	except Exception as e:
		print(f"Error updating client prompts: {e}")
		return False


def update_client_overall_prompt(client_id: str, overall_prompt: str, settings: Optional[Dict[str, str]] = None) -> bool:
	try:
		clients = load_all_clients()
		for client in clients:
			if client.get('client_id') == client_id:
				client['custom_overall_prompt'] = overall_prompt
				save_all_clients(clients)
				return True
		return False
	except Exception as e:
		print(f"Error updating client overall prompt: {e}")
		return False


def update_client_voice(client_id: str, voice_id: Optional[str]) -> bool:
	try:
		clients = load_all_clients()
		for client in clients:
			if client.get('client_id') == client_id:
				client['voice_id'] = voice_id
				save_all_clients(clients)
				return True
		return False
	except Exception as e:
		print(f"Error updating client voice: {e}")
		return False


