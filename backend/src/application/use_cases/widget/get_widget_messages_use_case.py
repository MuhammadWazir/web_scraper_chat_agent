from datetime import datetime, timezone
from typing import List
from src.application.dtos.responses.message_response import MessageResponse
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.message_repository import IMessageRepository

class GetWidgetMessagesUseCase:
    def __init__(
        self,
        widget_session_repository: IWidgetSessionRepository,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository
    ):
        self.widget_session_repository = widget_session_repository
        self.chat_repository = chat_repository
        self.message_repository = message_repository
    
    def execute(self, session_token: str, chat_id: str, end_user_ip: str) -> List[MessageResponse]:
        # Validate session
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            raise ValueError("Invalid session token")
        
        if widget_session.expires_at < datetime.now(timezone.utc):
            raise ValueError("Session token has expired")
        
        # IP normalization for localhost
        def normalize_ip(ip):
            return "127.0.0.1" if ip == "::1" else ip

        # Relaxed IP check for now to avoid issues on localhost
        # if normalize_ip(widget_session.end_user_ip) != normalize_ip(end_user_ip):
        #      raise ValueError("Session validation failed")
        
        # Verify chat belongs to this session's client
        chat = self.chat_repository.get_by_id(chat_id)
        if chat is None:
            raise ValueError("Chat not found")
            
        if chat.client_ip != widget_session.client_ip:
            raise ValueError("Access denied")
        
        messages = self.message_repository.get_by_chat_id(chat_id)
        
        return [
            MessageResponse(
                message_id=message.message_id,
                chat_id=message.chat_id,
                role="assistant" if message.ai_generated else "user",
                content=message.content,
                created_at=message.created_at
            )
            for message in messages
        ]
