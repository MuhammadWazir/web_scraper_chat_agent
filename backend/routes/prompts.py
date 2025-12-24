from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from configs.constants import PROMPTS
from services.prompts_service import (
	get_client_prompts_service,
	update_client_prompts_service,
	get_client_overall_prompt_service,
	update_client_overall_prompt_service,
	reset_client_overall_prompt_service
)
from dtos.prompts import (
	OverallPromptData,
	OverallPromptResponse
)

router = APIRouter(prefix="", tags=["prompts"])


@router.get("/prompt-templates")
async def get_prompt_templates():

    return {
        "templates": PROMPTS,
        "description": "These templates are used to generate client-specific prompts"
    }


@router.get("/client/{client_id}/prompts")
async def get_client_prompts(client_id: str):
    result = get_client_prompts_service(client_id)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    return result


@router.put("/client/{client_id}/prompts")
async def update_client_prompts_endpoint(client_id: str, prompts: Dict[str, Optional[str]]):
    updated_prompts = update_client_prompts_service(client_id, prompts)
    if not updated_prompts:
        raise HTTPException(status_code=404, detail="Client not found or update failed")
    
    return {
        "message": "Client prompts updated successfully",
        "prompts": updated_prompts
    }


@router.get("/client/{client_id}/overall-prompt", response_model=OverallPromptResponse)
async def get_client_overall_prompt(client_id: str):
    result = get_client_overall_prompt_service(client_id)
    if not result:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return OverallPromptResponse(**result)


@router.put("/client/{client_id}/overall-prompt")
async def update_client_overall_prompt_endpoint(client_id: str, update: OverallPromptData):
    success = update_client_overall_prompt_service(client_id, update.overall_prompt)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found or update failed")
    
    return {
        "message": "Overall prompt updated successfully"
    }


@router.post("/client/{client_id}/reset-overall-prompt")
async def reset_client_overall_prompt(client_id: str):
    default_prompt = reset_client_overall_prompt_service(client_id)
    if not default_prompt:
        raise HTTPException(status_code=404, detail="Client not found or reset failed")
    
    return {
        "message": "Overall prompt reset to default",
        "overall_prompt": default_prompt
    }

