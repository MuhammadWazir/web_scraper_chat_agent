from sqlalchemy import Column, String, DateTime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.database.config import Base


class ClientModel(Base):
    __tablename__ = "clients"

    client_id = Column(String, primary_key=True, index=True)
    client_ip = Column(String, nullable=False, index=True)
    client_name = Column(String, nullable=False)
    client_url = Column(String, nullable=False)
    api_key_hash = Column(String(255), unique=True, nullable=True, index=True)
    tools = Column(sa.JSON, nullable=True)
    system_prompt = Column(sa.Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    chats = relationship("ChatModel", back_populates="client", cascade="all, delete-orphan")
