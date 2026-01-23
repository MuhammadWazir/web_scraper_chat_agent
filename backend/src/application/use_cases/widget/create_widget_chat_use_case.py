from src.domain.entities.chat import Chat
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository


class CreateWidgetChatUseCase:
    def __init__(
        self,
        widget_session_repository: IWidgetSessionRepository,
        chat_repository: IChatRepository,
        client_repository: IClientRepository
    ):
        self.widget_session_repository = widget_session_repository
        self.chat_repository = chat_repository
        self.client_repository = client_repository
    
    def execute(self, session_token: str, end_user_ip: str) -> Chat:
        # Validate session
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            raise ValueError("Invalid session token")
        
        if not widget_session.validate(end_user_ip):
            raise ValueError("Session validation failed")
        
        # Verify client exists
        client = self.client_repository.get_by_id(widget_session.client_id)
        if client is None:
            raise ValueError(f"Client {widget_session.client_id} not found")
        
        # Create chat
        chat = Chat.create_new(
            client_id=widget_session.client_id,
            ip_address=end_user_ip
        )
        
        created_chat = self.chat_repository.create(chat)
        return created_chat
