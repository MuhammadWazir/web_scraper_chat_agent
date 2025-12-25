from sqlalchemy.orm import Session
from models.chat import Chat
from typing import Optional, List
import uuid


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, client_id: str, ip_address: str, title: Optional[str] = None) -> Chat:
        """Create a new chat"""
        chat_id = str(uuid.uuid4())
        chat = Chat(
            chat_id=chat_id,
            client_id=client_id,
            ip_address=ip_address,
            title=title
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_by_id(self, chat_id: str) -> Optional[Chat]:
        """Get chat by ID"""
        return self.db.query(Chat).filter(Chat.chat_id == chat_id).first()

    def get_by_client_id(self, client_id: str) -> List[Chat]:
        """Get all chats for a client"""
        return self.db.query(Chat).filter(Chat.client_id == client_id).order_by(Chat.created_at.desc()).all()

    def update(self, chat: Chat) -> Chat:
        """Update a chat"""
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def delete(self, chat_id: str) -> bool:
        """Delete a chat"""
        chat = self.get_by_id(chat_id)
        if chat:
            self.db.delete(chat)
            self.db.commit()
            return True
        return False

