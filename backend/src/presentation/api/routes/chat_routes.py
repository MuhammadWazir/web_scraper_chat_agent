"""Chat API routes"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from src.container import Container
from src.application.use_cases.chat.create_chat_use_case import CreateChatUseCase
from src.application.use_cases.chat.get_client_chats_use_case import GetClientChatsUseCase
from src.application.use_cases.chat.delete_chat_use_case import DeleteChatUseCase
from src.application.dtos.requests.create_chat_request import CreateChatRequest
from src.application.dtos.responses.chat_response import ChatResponse


router = APIRouter(prefix="", tags=["chats"])

# Global container instance
container = Container()


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    if request.client:
        return request.client.host
    return "unknown"


@router.post("/chats", response_model=ChatResponse)
async def create_chat(
    request: CreateChatRequest,
    http_request: Request,
    use_case: CreateChatUseCase = Depends(lambda: container.create_chat_use_case())
):
    """Create a new chat for a client"""
    try:
        client_ip = get_client_ip(http_request)
        result = use_case.execute(request, client_ip)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{client_id}/chats", response_model=List[ChatResponse])
async def get_client_chats(
    client_id: str,
    use_case: GetClientChatsUseCase = Depends(lambda: container.get_client_chats_use_case())
):
    """Get all chats for a client"""
    try:
        result = use_case.execute(client_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: str,
    use_case: DeleteChatUseCase = Depends(lambda: container.delete_chat_use_case())
):
    """Delete a chat"""
    try:
        success = use_case.execute(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
