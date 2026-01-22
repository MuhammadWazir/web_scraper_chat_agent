"""Message API routes"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any

from src.container import Container
from src.application.use_cases.message.send_message_use_case import SendMessageUseCase
from src.application.use_cases.message.get_chat_messages_use_case import GetChatMessagesUseCase
from src.application.dtos.requests.send_message_request import SendMessageRequest
from src.application.dtos.responses.message_response import MessageResponse


router = APIRouter(prefix="", tags=["messages"])

# Global container instance
container = Container()


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    if request.client:
        return request.client.host
    return "unknown"


@router.post("/chats/send-message")
async def send_message(
    request: SendMessageRequest,
    http_request: Request,
    use_case: SendMessageUseCase = Depends(lambda: container.send_message_use_case())
) -> Dict[str, Any]:
    """Send a message in a chat and get AI response. Creates chat if chat_id is not provided."""
    try:
        ip = get_client_ip(http_request)
        result = await use_case.execute(request, ip_address=ip)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: str,
    use_case: GetChatMessagesUseCase = Depends(lambda: container.get_chat_messages_use_case())
):
    """Get all messages for a chat"""
    try:
        result = use_case.execute(chat_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
