from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.domain.entities.widget_session import WidgetSession
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.infrastructure.database.models.widget_session_model import WidgetSessionModel


class WidgetSessionRepositoryImpl(IWidgetSessionRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, widget_session: WidgetSession) -> WidgetSession:
        db_session = WidgetSessionModel(
            session_token=widget_session.session_token,
            client_ip=widget_session.client_ip,
            end_user_ip=widget_session.end_user_ip,
            expires_at=widget_session.expires_at,
            created_at=widget_session.created_at
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        return self._to_entity(db_session)
    
    def get_by_token(self, session_token: str) -> Optional[WidgetSession]:
        db_session = self.db.query(WidgetSessionModel).filter(
            WidgetSessionModel.session_token == session_token
        ).first()
        
        if db_session is None:
            return None
        
        return self._to_entity(db_session)
    
    def update(self, widget_session: WidgetSession) -> WidgetSession:
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
        now = datetime.utcnow()
        result = self.db.query(WidgetSessionModel).filter(
            WidgetSessionModel.expires_at < now
        ).delete()
        self.db.commit()
        return result
    
    def _to_entity(self, model: WidgetSessionModel) -> WidgetSession:
        return WidgetSession(
            session_token=model.session_token,
            client_ip=model.client_ip,
            end_user_ip=model.end_user_ip,
            expires_at=model.expires_at,
            created_at=model.created_at
        )
