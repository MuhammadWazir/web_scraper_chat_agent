from typing import Dict, Any
from datetime import datetime, timezone
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository


class InitializeWidgetSessionUseCase:
    
    def __init__(self, widget_session_repository: IWidgetSessionRepository):
        self.widget_session_repository = widget_session_repository
    
    def execute(self, session_token: str, end_user_ip: str) -> Dict[str, Any]:
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            raise ValueError("Invalid session token")
        
        if widget_session.expires_at < datetime.now(timezone.utc):
            raise ValueError("Session token has expired")
        
        if widget_session.end_user_ip is not None:
            saved_ip = widget_session.end_user_ip
            current_ip = end_user_ip
            
            final_session = widget_session
        else:
            updated_session = widget_session.model_copy(update={"end_user_ip": end_user_ip})
            final_session = self.widget_session_repository.update(updated_session)
        
        return {
            "session_id": final_session.session_token,
            "expires_at": final_session.expires_at.isoformat()
        }
