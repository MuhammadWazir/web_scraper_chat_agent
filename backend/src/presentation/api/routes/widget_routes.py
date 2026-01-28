from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import List, Dict, Any

from src.container import Container
from src.application.use_cases.widget.initialize_widget_session_use_case import InitializeWidgetSessionUseCase
from src.application.use_cases.widget.get_widget_chats_use_case import GetWidgetChatsUseCase
from src.application.use_cases.widget.create_widget_chat_use_case import CreateWidgetChatUseCase
from src.application.use_cases.widget.delete_widget_chat_use_case import DeleteWidgetChatUseCase
from src.application.use_cases.widget.send_widget_message_use_case import SendWidgetMessageUseCase
from src.application.use_cases.widget.generate_widget_url_use_case import GenerateWidgetUrlUseCase
from src.application.dtos.responses.chat_response import ChatResponse
from src.application.dtos.requests.send_widget_message_request import SendWidgetMessageRequest


router = APIRouter(prefix="/widget", tags=["widget"])

container = Container()


@router.post("/generate-url")
async def generate_widget_url(
    x_api_key: str = Header(...),
    use_case: GenerateWidgetUrlUseCase = Depends(lambda: container.generate_widget_url_use_case())
):
    try:
        session_token = use_case.execute(x_api_key)
        
        return {
            "session_token": session_token
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/init/{session_token}")
async def initialize_widget_session(
    session_token: str,
    http_request: Request,
    use_case: InitializeWidgetSessionUseCase = Depends(lambda: container.initialize_widget_session_use_case())
) -> Dict[str, Any]:
    try:
        end_user_ip = http_request.client.host
        result = use_case.execute(session_token, end_user_ip)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_token}/chats", response_model=List[ChatResponse])
async def get_widget_chats(
    session_token: str,
    http_request: Request,
    use_case: GetWidgetChatsUseCase = Depends(lambda: container.get_widget_chats_use_case())
):
    try:
        end_user_ip = http_request.client.host
        chats = use_case.execute(session_token, end_user_ip)
        
        return [
            ChatResponse(
                chat_id=chat.chat_id,
                client_ip=chat.client_ip,
                title=chat.title,
                created_at=chat.created_at
            )
            for chat in chats
        ]
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_token}/chats", response_model=ChatResponse)
async def create_widget_chat(
    session_token: str,
    http_request: Request,
    use_case: CreateWidgetChatUseCase = Depends(lambda: container.create_widget_chat_use_case())
):
    try:
        end_user_ip = http_request.client.host
        chat = use_case.execute(session_token, end_user_ip)
        
        return ChatResponse(
            chat_id=chat.chat_id,
            client_ip=chat.client_ip,
            title=chat.title,
            created_at=chat.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_token}/chats/{chat_id}")
async def delete_widget_chat(
    session_token: str,
    chat_id: str,
    http_request: Request,
    use_case: DeleteWidgetChatUseCase = Depends(lambda: container.delete_widget_chat_use_case())
):
    try:
        end_user_ip = http_request.client.host
        success = use_case.execute(session_token, chat_id, end_user_ip)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {"message": "Chat deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_token}/chats/{chat_id}/messages")
async def send_widget_message(
    session_token: str,
    chat_id: str,
    request: SendWidgetMessageRequest,
    http_request: Request,
    use_case: SendWidgetMessageUseCase = Depends(lambda: container.send_widget_message_use_case())
):
    """
    Send a message in a widget chat.
    
    FIXED: Authorization token is now received from the request body only.
    The widget SDK sends it as part of the JSON payload.
    """
    try:
        end_user_ip = http_request.client.host
        
        # FIXED: Get auth_token from request body only (not from header)
        auth_token = request.authorization
        
        result = await use_case.execute(
            session_token=session_token,
            chat_id=chat_id,
            content=request.content,
            end_user_ip=end_user_ip,
            auth_token=auth_token
        )
        
        return {
            "message_id": result.message_id,
            "content": result.content,
            "ai_generated": result.ai_generated,
            "created_at": result.created_at
        }
    except ValueError as e:
        print("ValueError:", e)
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        print("Exception:", e)
        raise HTTPException(status_code=500, detail=str(e))