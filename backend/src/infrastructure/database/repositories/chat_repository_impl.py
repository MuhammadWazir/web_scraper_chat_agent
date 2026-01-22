"""Chat repository implementation - concrete SQLAlchemy implementation"""
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.entities.chat import Chat
from src.infrastructure.database.models.chat_model import ChatModel


class ChatRepositoryImpl(IChatRepository):
    """Concrete implementation of IChatRepository using SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: ChatModel) -> Chat:
        """Convert ORM model to domain entity"""
        return Chat(
            chat_id=model.chat_id,
            client_id=model.client_id,
            title=model.title,
            ip_address=model.ip_address,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: Chat) -> ChatModel:
        """Convert domain entity to ORM model"""
        return ChatModel(
            chat_id=entity.chat_id,
            client_id=entity.client_id,
            title=entity.title,
            ip_address=entity.ip_address,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def create(self, client_id: str, ip_address: str, title: Optional[str] = None) -> Chat:
        """Create a new chat"""
        chat_id = str(uuid.uuid4())
        model = ChatModel(
            chat_id=chat_id,
            client_id=client_id,
            ip_address=ip_address,
            title=title
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, chat_id: str) -> Optional[Chat]:
        """Get chat by ID"""
        model = self.db.query(ChatModel).filter(ChatModel.chat_id == chat_id).first()
        return self._to_entity(model) if model else None
    
    def get_by_client_id(self, client_id: str) -> List[Chat]:
        """Get all chats for a client"""
        models = self.db.query(ChatModel).filter(ChatModel.client_id == client_id).all()
        return [self._to_entity(model) for model in models]
    
    def update(self, chat: Chat) -> Chat:
        """Update a chat"""
        model = self.db.query(ChatModel).filter(ChatModel.chat_id == chat.chat_id).first()
        if model:
            model.title = chat.title
            model.updated_at = chat.updated_at
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        raise ValueError(f"Chat with ID {chat.chat_id} not found")
    
    def delete(self, chat_id: str) -> bool:
        """Delete a chat"""
        model = self.db.query(ChatModel).filter(ChatModel.chat_id == chat_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False
