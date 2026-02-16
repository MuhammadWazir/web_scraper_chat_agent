from datetime import datetime, timezone
from typing import List
from src.domain.entities.chat import Chat
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository

class GetWidgetChatsUseCase:
    def __init__(
        self,
        widget_session_repository: IWidgetSessionRepository,
        chat_repository: IChatRepository
    ):
        self.widget_session_repository = widget_session_repository
        self.chat_repository = chat_repository
    
    def execute(self, session_token: str, end_user_ip: str) -> List[Chat]:
        # Validate session
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            raise ValueError("Invalid session token")
        
        if widget_session.expires_at < datetime.now(timezone.utc):
            raise ValueError("Session token has expired")
        
        if widget_session.end_user_ip is not None and widget_session.end_user_ip != end_user_ip:
             raise ValueError("Session validation failed")
        
        chats = self.chat_repository.get_by_client_id(widget_session.client_id)
        
        # Filter by end-user IP
        filtered_chats = [chat for chat in chats if chat.ip_address == end_user_ip]
        
        return filtered_chats
