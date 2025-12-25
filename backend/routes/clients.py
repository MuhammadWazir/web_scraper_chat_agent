from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from use_cases.create_client_use_case import CreateClientUseCase
from use_cases.query_client_use_case import QueryClientUseCase
from use_cases.create_chat_use_case import CreateChatUseCase
from use_cases.get_client_chats_use_case import GetClientChatsUseCase
from use_cases.delete_chat_use_case import DeleteChatUseCase
from use_cases.send_message_use_case import SendMessageUseCase
from use_cases.get_chat_messages_use_case import GetChatMessagesUseCase
from dtos.create_client_dto import CreateClientDTO
from dtos.query_client_dto import QueryClientDTO
from dtos.create_chat_dto import CreateChatDTO
from dtos.send_message_dto import SendMessageDTO

router = APIRouter(prefix="", tags=["clients"])


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    if request.client:
        return request.client.host
    return "unknown"


@router.post("/create-client")
async def create_client(
    request: CreateClientDTO,
    db: Session = Depends(get_db)
):
    """Create a new client and build RAG pipeline"""
    use_case = CreateClientUseCase(db)
    try:
        result = await use_case.execute(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query-client")
async def query_client(
    request: QueryClientDTO,
    chat_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Query a client using RAG pipeline (deprecated - use send-message instead)"""
    use_case = QueryClientUseCase(db)
    try:
        client_ip = get_client_ip(http_request)
        result = await use_case.execute(request, chat_id, client_ip)
        return result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients")
async def get_all_clients(db: Session = Depends(get_db)):
    """Get all clients"""
    from repositories.client_repository import ClientRepository
    repository = ClientRepository(db)
    clients = repository.get_all()
    return [
        {
            "client_id": client.client_id,
            "company_name": client.client_name,
            "website_url": client.client_url,
            "created_at": client.created_at.isoformat() if client.created_at else None
        }
        for client in clients
    ]


@router.get("/clients/{client_id}")
async def get_client(client_id: str, db: Session = Depends(get_db)):
    """Get a client by ID"""
    from repositories.client_repository import ClientRepository
    repository = ClientRepository(db)
    client = repository.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {
        "client_id": client.client_id,
        "company_name": client.client_name,
        "website_url": client.client_url,
        "created_at": client.created_at.isoformat() if client.created_at else None
    }


@router.post("/chats")
async def create_chat(
    request: CreateChatDTO,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Create a new chat for a client"""
    use_case = CreateChatUseCase(db)
    try:
        client_ip = get_client_ip(http_request)
        result = use_case.execute(request, client_ip)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients/{client_id}/chats")
async def get_client_chats(client_id: str, db: Session = Depends(get_db)):
    """Get all chats for a client"""
    use_case = GetClientChatsUseCase(db)
    try:
        result = use_case.execute(client_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    """Delete a chat"""
    use_case = DeleteChatUseCase(db)
    try:
        success = use_case.execute(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chats/send-message")
async def send_message(
    request: SendMessageDTO,
    db: Session = Depends(get_db)
):
    """Send a message in a chat and get AI response"""
    use_case = SendMessageUseCase(db)
    try:
        result = await use_case.execute(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: str, db: Session = Depends(get_db)):
    """Get all messages for a chat"""
    use_case = GetChatMessagesUseCase(db)
    try:
        result = use_case.execute(chat_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
