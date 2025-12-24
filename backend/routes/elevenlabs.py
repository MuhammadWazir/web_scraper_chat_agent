from fastapi import APIRouter, HTTPException
from typing import Optional
from services.elevenlabs_service import get_signed_url_service, list_voices_service

router = APIRouter(prefix="", tags=["elevenlabs"])

@router.get("/signed-url")
async def get_signed_url(voice_id: Optional[str] = None):
	try:
		return await get_signed_url_service(voice_id)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def list_voices():
	try:
		return await list_voices_service()
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


