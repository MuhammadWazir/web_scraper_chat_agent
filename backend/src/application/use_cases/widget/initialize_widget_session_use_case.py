from typing import Dict, Any
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository


class InitializeWidgetSessionUseCase:
    
    def __init__(self, widget_session_repository: IWidgetSessionRepository):
        self.widget_session_repository = widget_session_repository
    
    def execute(self, session_token: str, end_user_ip: str) -> Dict[str, Any]:
        # Get the widget session
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            raise ValueError("Invalid session token")
        
        # Check if expired
        if widget_session.is_expired():
            raise ValueError("Session token has expired")
        
        # Bind to user IP (will raise if already bound)
        widget_session.bind_to_user(end_user_ip)
        
        # Update in database
        updated_session = self.widget_session_repository.update(widget_session)
        
        return {
            "session_id": updated_session.session_token,
            "client_id": updated_session.client_id,
            "widget_config": {
                "expires_at": updated_session.expires_at.isoformat()
            }
        }
