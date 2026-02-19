from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any

from src.container import Container
from src.application.use_cases.widget.initialize_widget_session_use_case import InitializeWidgetSessionUseCase
from src.application.use_cases.widget.get_widget_chats_use_case import GetWidgetChatsUseCase
from src.application.use_cases.widget.create_widget_chat_use_case import CreateWidgetChatUseCase
from src.application.use_cases.widget.delete_widget_chat_use_case import DeleteWidgetChatUseCase
from src.application.use_cases.widget.send_widget_message_use_case import SendWidgetMessageUseCase
from src.application.use_cases.widget.generate_widget_url_use_case import GenerateWidgetUrlUseCase
from src.application.use_cases.widget.get_widget_messages_use_case import GetWidgetMessagesUseCase
from src.application.dtos.responses.chat_response import ChatResponse
from src.application.dtos.requests.send_widget_message_request import SendWidgetMessageRequest


router = APIRouter(prefix="/widget", tags=["widget"])

container = Container()


def get_client_ip(request: Request) -> str:
    """Get the real client IP from X-Forwarded-For header or fallback to client.host."""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # Take the first IP (original client)
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


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
        end_user_ip = get_client_ip(http_request)
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
        end_user_ip = get_client_ip(http_request)
        chats = use_case.execute(session_token, end_user_ip)
        
        return [
            ChatResponse(
                chat_id=chat.chat_id,
                client_id=chat.client_id,
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
        end_user_ip = get_client_ip(http_request)
        chat = use_case.execute(session_token, end_user_ip)
        
        return ChatResponse(
            chat_id=chat.chat_id,
            client_id=chat.client_id,
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
        end_user_ip = get_client_ip(http_request)
        success = use_case.execute(session_token, chat_id, end_user_ip)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {"message": "Chat deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_token}/chats/{chat_id}/messages-stream")
async def send_widget_message_stream(
    session_token: str,
    chat_id: str,
    request: SendWidgetMessageRequest,
    http_request: Request,
    use_case: SendWidgetMessageUseCase = Depends(lambda: container.send_widget_message_use_case())
):
    try:
        end_user_ip = get_client_ip(http_request)
        auth_token = request.authorization
        
        async def event_generator():
            async for chunk in use_case.execute_stream(
                session_token=session_token,
                chat_id=chat_id,
                content=request.content,
                end_user_ip=end_user_ip,
                auth_token=auth_token,
                is_follow_up=request.is_follow_up
            ):
                yield chunk + "\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_token}/chats/{chat_id}/messages", response_model=List[Any])
async def get_widget_chat_messages(
    session_token: str,
    chat_id: str,
    http_request: Request,
    use_case: GetWidgetMessagesUseCase = Depends(lambda: container.get_widget_messages_use_case())
):
    try:
        end_user_ip = get_client_ip(http_request)
        messages = use_case.execute(session_token, chat_id, end_user_ip)
        return messages
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
