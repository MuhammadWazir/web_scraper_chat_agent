from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(String, primary_key=True, index=True)
    client_name = Column(String, nullable=False)
    client_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    chats = relationship("Chat", back_populates="client", cascade="all, delete-orphan")

