from sqlalchemy.orm import Session
from models.message import Message
from typing import Optional, List
import uuid


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, chat_id: str, message_content: str, ai_generated: bool = False) -> Message:
        """Create a new message"""
        message_id = str(uuid.uuid4())
        message = Message(
            message_id=message_id,
            chat_id=chat_id,
            message_content=message_content,
            ai_generated=ai_generated
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID"""
        return self.db.query(Message).filter(Message.message_id == message_id).first()

    def get_by_chat_id(self, chat_id: str) -> List[Message]:
        """Get all messages for a chat"""
        return self.db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at.asc()).all()
    
    def get_last_messages(self, chat_id: str, limit: int = 6) -> List[Message]:
        """Get the last N messages for a chat, ordered by creation time (oldest first)"""
        return self.db.query(Message).filter(
            Message.chat_id == chat_id
        ).order_by(Message.created_at.desc()).limit(limit).all()[::-1]

    def update(self, message: Message) -> Message:
        """Update a message"""
        self.db.commit()
        self.db.refresh(message)
        return message

    def delete(self, message_id: str) -> bool:
        """Delete a message"""
        message = self.get_by_id(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False

