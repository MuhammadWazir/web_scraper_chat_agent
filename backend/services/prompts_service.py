from typing import Optional, Dict
from configs.constants import DEFAULT_OVERALL_PROMPT_TEMPLATE
from repositories.clients_repository import (
	get_client_by_url_slug,
	update_client_prompts,
	update_client_overall_prompt
)


def _get_client(url_slug: str) -> Optional[Dict]:
	"""Get client by URL slug (company name)"""
	return get_client_by_url_slug(url_slug)


def get_client_prompts_service(client_id: str) -> Optional[Dict]:
	client = _get_client(client_id)
	if not client:
		return None
	
	return {
		"client_id": client_id,
		"company_name": client.get("company_name"),
		"prompts": client.get("prompts", {})
	}


def update_client_prompts_service(client_id: str, new_prompts: Dict[str, Optional[str]]) -> Optional[Dict]:
	client = _get_client(client_id)
	if not client:
		return None
	
	current_prompts = client.get("prompts", {})
	updated_prompts = {**current_prompts, **new_prompts}
	
	client_id = client.get("client_id")
	success = update_client_prompts(client_id, updated_prompts)
	if not success:
		return None
	
	return updated_prompts


def get_client_overall_prompt_service(client_id: str) -> Optional[Dict]:
	client = _get_client(client_id)
	if not client:
		return None
	
	custom_prompt = client.get("custom_overall_prompt")
	is_custom = custom_prompt is not None
	prompt = custom_prompt if is_custom else DEFAULT_OVERALL_PROMPT_TEMPLATE
	
	return {
		"overall_prompt": prompt,
		"is_custom": is_custom
	}


def update_client_overall_prompt_service(client_id: str, overall_prompt: str) -> bool:
	client = _get_client(client_id)
	if not client:
		return False
	
	# Use the actual client_id from the found client for updates
	client_id = client.get("client_id")
	return update_client_overall_prompt(client_id, overall_prompt, None)


def reset_client_overall_prompt_service(client_id: str) -> Optional[str]:
	client = _get_client(client_id)
	if not client:
		return None
	
	# Use the actual client_id from the found client for updates
	client_id = client.get("client_id")
	success = update_client_overall_prompt(client_id, None)
	if not success:
		return None
	
	return DEFAULT_OVERALL_PROMPT_TEMPLATE

