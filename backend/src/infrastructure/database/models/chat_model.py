from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.database.config import Base


class ChatModel(Base):
    __tablename__ = "chats"

    chat_id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False, index=True)
    ip_address = Column(String, nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    client = relationship("ClientModel", back_populates="chats")
    messages = relationship("MessageModel", back_populates="chat", cascade="all, delete-orphan", order_by="MessageModel.created_at")
