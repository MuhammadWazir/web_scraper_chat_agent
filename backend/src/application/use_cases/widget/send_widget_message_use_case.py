from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.message_repository import IMessageRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.infrastructure.services.RagService import RAGService
from src.infrastructure.services.ChatTitleService import ChatTitleService
from src.domain.entities.message import Message


class SendWidgetMessageUseCase:
    def __init__(
        self,
        widget_session_repository: IWidgetSessionRepository,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository,
        client_repository: IClientRepository,
        rag_service: RAGService,
        chat_title_service: ChatTitleService
    ):
        self.widget_session_repository = widget_session_repository
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.client_repository = client_repository
        self.rag_service = rag_service
        self.chat_title_service = chat_title_service
    
    async def execute(self, session_token: str, chat_id: str, content: str, end_user_ip: str):
        # Validate session
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            raise ValueError("Invalid session token")
        
        if not widget_session.validate(end_user_ip):
            raise ValueError("Session validation failed")
        
        # Verify chat exists and belongs to this user
        chat = self.chat_repository.get_by_id(chat_id)
        if chat is None:
            raise ValueError("Chat not found")
        
        if chat.ip_address != end_user_ip:
            raise ValueError("Unauthorized access to chat")
        
        # Get client for RAG context
        client = self.client_repository.get_by_id(chat.client_id)
        if client is None:
            raise ValueError("Client not found")
        
        # Create user message
        user_message = Message.create_user_message(chat_id, content)
        self.message_repository.create(user_message)
        
        # Generate AI response using RAG
        ai_response = await self.rag_service.generate_response(
            client_id=client.client_id,
            query=content
        )
        
        # Create AI message
        ai_message = Message.create_ai_message(chat_id, ai_response)
        created_ai_message = self.message_repository.create(ai_message)
        
        # Update chat title if first message
        messages = self.message_repository.get_by_chat_id(chat_id)
        if len(messages) <= 2:  # User + AI message
            title = await self.chat_title_service.generate_title(content, ai_response)
            chat.title = title
            self.chat_repository.update(chat)
        
        return created_ai_message
