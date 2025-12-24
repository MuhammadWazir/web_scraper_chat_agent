from fastapi import APIRouter, HTTPException
from services.clients_service import (
	create_chat_agent_service,
	get_all_clients_service,
	get_client_by_url_slug_service,
	get_client_voice_service,
	update_client_voice_service,
)
from dtos.chat_agent import ChatAgentRequest, ChatAgentResponse
from dtos.voice import VoiceUpdate

router = APIRouter(prefix="", tags=["clients"])


@router.get("/clients")
async def get_all_clients():
	"""Get all clients"""
	return get_all_clients_service()


@router.get("/client/{client_id}")
async def get_client(client_id: str):
	client_data = get_client_by_url_slug_service(client_id)
	if not client_data:
		raise HTTPException(status_code=404, detail="Client not found")
	return client_data

@router.post("/create-chat-agent", response_model=ChatAgentResponse)
async def create_chat_agent(request: ChatAgentRequest):
	result = await create_chat_agent_service(
		website_url=str(request.website_url),
		target_audience=request.target_audience,
		company_name=request.company_name,
	)
	return ChatAgentResponse(
		client_id=result["client_id"],
		url=result["url_slug"],
	)



