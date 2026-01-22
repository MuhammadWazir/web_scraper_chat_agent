"""Message repository implementation - concrete SQLAlchemy implementation"""
from sqlalchemy.orm import Session
from typing import List, Literal
import uuid

from src.domain.abstractions.repositories.message_repository import IMessageRepository
from src.domain.entities.message import Message
from src.infrastructure.database.models.message_model import MessageModel


class MessageRepositoryImpl(IMessageRepository):
    """Concrete implementation of IMessageRepository using SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: MessageModel) -> Message:
        """Convert ORM model to domain entity"""
        # Map ai_generated boolean to role
        role = "assistant" if model.ai_generated else "user"
        return Message(
            message_id=model.message_id,
            chat_id=model.chat_id,
            role=role,
            content=model.message_content,
            created_at=model.created_at
        )
    
    def _to_model(self, entity: Message) -> MessageModel:
        """Convert domain entity to ORM model"""
        # Map role to ai_generated boolean
        ai_generated = (entity.role == "assistant")
        return MessageModel(
            message_id=entity.message_id,
            chat_id=entity.chat_id,
            message_content=entity.content,
            ai_generated=ai_generated,
            created_at=entity.created_at
        )
    
    def create(self, chat_id: str, role: Literal["user", "assistant"], content: str) -> Message:
        """Create a new message"""
        message_id = str(uuid.uuid4())
        ai_generated = (role == "assistant")
        model = MessageModel(
            message_id=message_id,
            chat_id=chat_id,
            message_content=content,
            ai_generated=ai_generated
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, message_id: str) -> Message:
        """Get message by ID"""
        model = self.db.query(MessageModel).filter(MessageModel.message_id == message_id).first()
        if not model:
            raise ValueError(f"Message with ID {message_id} not found")
        return self._to_entity(model)
    
    def get_by_chat_id(self, chat_id: str) -> List[Message]:
        """Get all messages for a chat"""
        models = self.db.query(MessageModel).filter(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at).all()
        return [self._to_entity(model) for model in models]
    
    def delete_by_chat_id(self, chat_id: str) -> bool:
        """Delete all messages for a chat"""
        deleted = self.db.query(MessageModel).filter(MessageModel.chat_id == chat_id).delete()
        self.db.commit()
        return deleted > 0
