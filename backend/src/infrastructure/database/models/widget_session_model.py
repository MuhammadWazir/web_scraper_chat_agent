from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.infrastructure.database.config import Base


class WidgetSessionModel(Base):
    __tablename__ = "widget_sessions"

    session_token = Column(String, primary_key=True, index=True)
    client_ip = Column(String, ForeignKey("clients.client_ip", ondelete="CASCADE"), nullable=False, index=True)
    end_user_ip = Column(String(45), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    client = relationship("ClientModel", backref="widget_sessions")
