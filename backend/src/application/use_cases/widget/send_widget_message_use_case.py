from datetime import datetime, timezone
import uuid
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.message_repository import IMessageRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.abstractions.services.rag_service import IRAGService
from src.domain.abstractions.services.chat_title_service import IChatTitleService
from src.domain.entities.message import Message


class SendWidgetMessageUseCase:
    def __init__(
        self,
        widget_session_repository: IWidgetSessionRepository,
        chat_repository: IChatRepository,
        message_repository: IMessageRepository,
        client_repository: IClientRepository,
        rag_service: IRAGService,
        chat_title_service: IChatTitleService
    ):
        self.widget_session_repository = widget_session_repository
        self.chat_repository = chat_repository
        self.message_repository = message_repository
        self.client_repository = client_repository
        self.rag_service = rag_service
        self.chat_title_service = chat_title_service
    
    async def execute(self, session_token: str, chat_id: str, content: str, end_user_ip: str, auth_token: str = None):
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            raise ValueError("Invalid session token")
        
        if widget_session.expires_at < datetime.now(timezone.utc) or widget_session.end_user_ip != end_user_ip:
            raise ValueError("Session validation failed")
        
        chat = self.chat_repository.get_by_id(chat_id)
        if chat is None:
            raise ValueError("Chat not found")
        
        if chat.ip_address != end_user_ip:
            raise ValueError("Unauthorized access to chat")
        
        client = self.client_repository.get_by_id(chat.client_ip)
        if client is None:
            raise ValueError("Client not found")
            
        existing_messages = self.message_repository.get_by_chat_id(chat.chat_id)
        is_first_message = len(existing_messages) == 0
        
        recent_messages = existing_messages[-6:] if len(existing_messages) >= 6 else existing_messages
        
        chat_history = []
        i = 0
        while i < len(recent_messages) - 1:
            if not recent_messages[i].ai_generated and recent_messages[i + 1].ai_generated:
                chat_history.append({
                    "user": recent_messages[i].content,
                    "assistant": recent_messages[i + 1].content
                })
                i += 2
            else:
                i += 1
        
        now = datetime.now(timezone.utc)
        user_message_entity = Message(
            message_id=str(uuid.uuid4()),
            chat_id=chat_id,
            content=content,
            ai_generated=False,
            created_at=now,
            updated_at=now
        )
        user_message = self.message_repository.create(user_message_entity)
        
        if is_first_message:
            title = await self.chat_title_service.generate_title(content)
            updated_chat = chat.model_copy(update={"title": title, "updated_at": datetime.now(timezone.utc)})
            self.chat_repository.update(updated_chat)
        
        ai_response = await self.rag_service.query(
            question=content, 
            company_name=client.client_name, 
            chat_history=chat_history,
            tools=client.tools,
            auth_token=auth_token
        )
        
        ai_message_entity = Message(
            message_id=str(uuid.uuid4()),
            chat_id=chat_id,
            content=ai_response,
            ai_generated=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        created_ai_message = self.message_repository.create(ai_message_entity)
        
        return created_ai_message