from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String, primary_key=True, index=True)
    chat_id = Column(String, ForeignKey("chats.chat_id", ondelete="CASCADE"), nullable=False, index=True)
    message_content = Column(Text, nullable=False)
    ai_generated = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    chat = relationship("Chat", back_populates="messages")

