from sqlalchemy.orm import Session
from typing import List, Dict

from src.domain.abstractions.repositories.message_repository import IMessageRepository
from src.domain.entities.message import Message
from src.infrastructure.database.models.message_model import MessageModel


class MessageRepository(IMessageRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: MessageModel) -> Message:
        return Message(
            message_id=model.message_id,
            chat_id=model.chat_id,
            content=model.message_content,
            ai_generated=model.ai_generated,
            created_at=model.created_at,
            updated_at=model.created_at
        )
    
    def _to_model(self, entity: Message) -> MessageModel:
        return MessageModel(
            message_id=entity.message_id,
            chat_id=entity.chat_id,
            message_content=entity.content,
            ai_generated=entity.ai_generated,
            created_at=entity.created_at
        )
    
    def create(self, message: Message) -> Message:
        model = self._to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, message_id: str) -> Message:
        model = self.db.query(MessageModel).filter(MessageModel.message_id == message_id).first()
        if not model:
            raise ValueError(f"Message with ID {message_id} not found")
        return self._to_entity(model)
    
    def get_by_chat_id(self, chat_id: str) -> List[Message]:
        models = self.db.query(MessageModel).filter(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at).all()
        return [self._to_entity(model) for model in models]
    
    def get_chat_history(self, chat_id: str, limit: int = 20) -> List[Dict[str, str]]:
        models = (
            self.db.query(MessageModel)
            .filter(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
            .all()
        )
        
        messages = [self._to_entity(model) for model in reversed(models)]
        
        chat_history = []
        i = 0
        while i < len(messages) - 1:
            if not messages[i].ai_generated and messages[i + 1].ai_generated:
                chat_history.append({
                    "user": messages[i].content,
                    "assistant": messages[i + 1].content
                })
                i += 2
            else:
                i += 1
        
        return chat_history
    
    def delete_by_chat_id(self, chat_id: str) -> bool:
        deleted = self.db.query(MessageModel).filter(MessageModel.chat_id == chat_id).delete()
        self.db.commit()
        return deleted > 0
