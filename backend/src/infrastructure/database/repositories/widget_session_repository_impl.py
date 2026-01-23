"""Widget session repository implementation"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.domain.entities.widget_session import WidgetSession
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.infrastructure.database.models.widget_session_model import WidgetSessionModel


class WidgetSessionRepositoryImpl(IWidgetSessionRepository):
    """SQLAlchemy implementation of widget session repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, widget_session: WidgetSession) -> WidgetSession:
        """Create a new widget session"""
        db_session = WidgetSessionModel(
            session_token=widget_session.session_token,
            client_id=widget_session.client_id,
            end_user_ip=widget_session.end_user_ip,
            expires_at=widget_session.expires_at,
            created_at=widget_session.created_at
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        return self._to_entity(db_session)
    
    def get_by_token(self, session_token: str) -> Optional[WidgetSession]:
        """Get widget session by token"""
        db_session = self.db.query(WidgetSessionModel).filter(
            WidgetSessionModel.session_token == session_token
        ).first()
        
        if db_session is None:
            return None
        
        return self._to_entity(db_session)
    
    def update(self, widget_session: WidgetSession) -> WidgetSession:
        """Update widget session (e.g., bind to IP address)"""
        db_session = self.db.query(WidgetSessionModel).filter(
            WidgetSessionModel.session_token == widget_session.session_token
        ).first()
        
        if db_session is None:
            raise ValueError(f"Widget session {widget_session.session_token} not found")
        
        db_session.end_user_ip = widget_session.end_user_ip
        db_session.expires_at = widget_session.expires_at
        
        self.db.commit()
        self.db.refresh(db_session)
        
        return self._to_entity(db_session)
    
    def delete_expired(self) -> int:
        """Delete all expired sessions"""
        now = datetime.utcnow()
        result = self.db.query(WidgetSessionModel).filter(
            WidgetSessionModel.expires_at < now
        ).delete()
        self.db.commit()
        return result
    
    def _to_entity(self, model: WidgetSessionModel) -> WidgetSession:
        """Convert database model to domain entity"""
        return WidgetSession(
            session_token=model.session_token,
            client_id=model.client_id,
            end_user_ip=model.end_user_ip,
            expires_at=model.expires_at,
            created_at=model.created_at
        )
