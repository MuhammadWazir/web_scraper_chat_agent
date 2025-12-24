from fastapi import APIRouter, HTTPException
from services.clients_service import (
	create_voice_agent_service,
	get_all_clients_service,
	get_client_by_url_slug_service,
	get_client_voice_service,
	update_client_voice_service,
)
from dtos.voice_agent import VoiceAgentRequest, VoiceAgentResponse
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

@router.post("/create-voice-agent", response_model=VoiceAgentResponse)
async def create_voice_agent(request: VoiceAgentRequest):
	result = await create_voice_agent_service(
		website_url=str(request.website_url),
		target_audience=request.target_audience,
		company_name=request.company_name,
	)
	return VoiceAgentResponse(
		client_id=result["client_id"],
		url=result["url_slug"],
	)


@router.get("/client/{client_id}/voice")
async def get_client_voice(client_id: str):
	voice_id = get_client_voice_service(client_id)
	if voice_id is None:
		return {"voice_id": None}
	return {"voice_id": voice_id}


@router.put("/client/{client_id}/voice")
async def update_client_voice(client_id: str, update: VoiceUpdate):
	success = update_client_voice_service(client_id, update.voice_id)
	if not success:
		raise HTTPException(status_code=404, detail="Client not found or update failed")
	return {"message": "Voice updated"}

