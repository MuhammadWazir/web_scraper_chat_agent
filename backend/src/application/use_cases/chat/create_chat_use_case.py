"""Create chat use case - with dependency injection"""
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.application.dtos.requests.create_chat_request import CreateChatRequest
from src.application.dtos.responses.chat_response import ChatResponse


class CreateChatUseCase:
    """Use case for creating a new chat"""
    
    def __init__(self, chat_repository: IChatRepository, client_repository: IClientRepository):
        self.chat_repository = chat_repository
        self.client_repository = client_repository

    def execute(self, request: CreateChatRequest, ip_address: str) -> ChatResponse:
        """Create a new chat for a client"""
        # Verify client exists
        client = self.client_repository.get_by_id(request.client_id)
        if not client:
            raise ValueError(f"Client with ID {request.client_id} not found")
        
        # Create chat
        import uuid
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        from src.domain.entities.chat import Chat
        chat_entity = Chat(
            chat_id=str(uuid.uuid4()),
            client_ip=request.client_id,
            ip_address=ip_address,
            title=None,
            created_at=now,
            updated_at=now
        )
        chat = self.chat_repository.create(chat_entity)
        
        return ChatResponse(
            chat_id=chat.chat_id,
            client_ip=chat.client_ip,
            title=chat.title,
            created_at=chat.created_at
        )
