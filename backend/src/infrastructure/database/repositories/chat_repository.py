from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.entities.chat import Chat
from src.infrastructure.database.models.chat_model import ChatModel


class ChatRepository(IChatRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: ChatModel) -> Chat:
        return Chat(
            chat_id=model.chat_id,
            client_ip=model.client_ip,
            ip_address=model.ip_address,
            title=model.title,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: Chat) -> ChatModel:
        return ChatModel(
            chat_id=entity.chat_id,
            client_ip=entity.client_ip,
            ip_address=entity.ip_address,
            title=entity.title,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def create(self, client_id: str, ip_address: str, title: Optional[str] = None) -> Chat:
        now = datetime.now(timezone.utc)
        chat = Chat(
            chat_id=str(uuid.uuid4()),
            client_ip=client_id,
            ip_address=ip_address,
            title=title,
            created_at=now,
            updated_at=now
        )
        model = self._to_model(chat)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, chat_id: str) -> Optional[Chat]:
        model = self.db.query(ChatModel).filter(ChatModel.chat_id == chat_id).first()
        return self._to_entity(model) if model else None
    
    def get_by_client_id(self, client_ip: str) -> List[Chat]:
        models = self.db.query(ChatModel).filter(ChatModel.client_ip == client_ip).all()
        return [self._to_entity(model) for model in models]
    
    def update(self, chat: Chat) -> Chat:
        model = self.db.query(ChatModel).filter(ChatModel.chat_id == chat.chat_id).first()
        if model:
            model.title = chat.title
            model.updated_at = chat.updated_at
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        raise ValueError(f"Chat with ID {chat.chat_id} not found")
    
    def delete(self, chat_id: str) -> bool:
        model = self.db.query(ChatModel).filter(ChatModel.chat_id == chat_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False
