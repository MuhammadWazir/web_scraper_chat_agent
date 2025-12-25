from repositories.chat_repository import ChatRepository
from repositories.client_repository import ClientRepository
from sqlalchemy.orm import Session


class GetClientChatsUseCase:
    def __init__(self, db: Session):
        self.chat_repository = ChatRepository(db)
        self.client_repository = ClientRepository(db)

    def execute(self, client_id: str) -> list:
        """Get all chats for a client"""
        # Verify client exists
        client = self.client_repository.get_by_id(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        
        # Get chats
        chats = self.chat_repository.get_by_client_id(client_id)
        
        return [
            {
                "chat_id": chat.chat_id,
                "client_id": chat.client_id,
                "title": chat.title,
                "ip_address": chat.ip_address,
                "created_at": chat.created_at.isoformat() if chat.created_at else None,
                "updated_at": chat.updated_at.isoformat() if chat.updated_at else None
            }
            for chat in chats
        ]

