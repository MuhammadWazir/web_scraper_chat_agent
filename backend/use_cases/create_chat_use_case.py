from repositories.chat_repository import ChatRepository
from repositories.client_repository import ClientRepository
from dtos.create_chat_dto import CreateChatDTO
from sqlalchemy.orm import Session
from typing import Optional


class CreateChatUseCase:
    def __init__(self, db: Session):
        self.chat_repository = ChatRepository(db)
        self.client_repository = ClientRepository(db)

    def execute(self, dto: CreateChatDTO, ip_address: str) -> dict:
        """Create a new chat for a client"""
        # Verify client exists
        client = self.client_repository.get_by_id(dto.client_id)
        if not client:
            raise ValueError(f"Client with ID {dto.client_id} not found")
        
        # Create chat
        chat = self.chat_repository.create(
            client_id=dto.client_id,
            ip_address=ip_address,
            title=dto.title
        )
        
        return {
            "chat_id": chat.chat_id,
            "client_id": chat.client_id,
            "title": chat.title,
            "created_at": chat.created_at.isoformat() if chat.created_at else None
        }

