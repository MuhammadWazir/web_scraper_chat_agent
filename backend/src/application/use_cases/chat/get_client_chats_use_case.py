"""Get client chats use case - with dependency injection"""
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.application.dtos.responses.chat_response import ChatResponse
from typing import List


class GetClientChatsUseCase:
    """Use case for getting all chats for a client"""
    
    def __init__(self, chat_repository: IChatRepository, client_repository: IClientRepository):
        self.chat_repository = chat_repository
        self.client_repository = client_repository

    def execute(self, client_id: str) -> List[ChatResponse]:
        """Get all chats for a client"""
        # Verify client exists
        client = self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        
        # Get chats
        chats = self.chat_repository.get_by_client_id(client_id)
        
        return [
            ChatResponse(
                chat_id=chat.chat_id,
                client_id=chat.client_id,
                title=chat.title,
                created_at=chat.created_at
            )
            for chat in chats
        ]
