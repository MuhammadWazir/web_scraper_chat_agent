from datetime import datetime, timezone
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository

class DeleteWidgetChatUseCase:
    def __init__(
        self,
        widget_session_repository: IWidgetSessionRepository,
        chat_repository: IChatRepository
    ):
        self.widget_session_repository = widget_session_repository
        self.chat_repository = chat_repository
    
    def execute(self, session_token: str, chat_id: str, end_user_ip: str) -> bool:
        # Validate session
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            raise ValueError("Invalid session token")
        
        if widget_session.expires_at < datetime.now(timezone.utc):
            raise ValueError("Session token has expired")
            
        if widget_session.end_user_ip is not None and widget_session.end_user_ip != end_user_ip:
            raise ValueError("Session validation failed")
        
        # Verify chat belongs to this user
        chat = self.chat_repository.get_by_id(chat_id)
        if chat is None:
            raise ValueError("Chat not found")
        
        if chat.ip_address != end_user_ip:
            raise ValueError("Unauthorized access to chat")
        
        # Delete chat
        return self.chat_repository.delete(chat_id)
