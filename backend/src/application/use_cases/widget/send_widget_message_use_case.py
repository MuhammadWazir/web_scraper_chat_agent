import uuid
import json
from datetime import datetime, timezone
from typing import AsyncIterator
from src.domain.entities.message import Message
from src.domain.abstractions.repositories.message_repository import IMessageRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.services.rag_service import IRAGService
from src.domain.abstractions.services.chat_title_service import IChatTitleService


class SendWidgetMessageUseCase:
    """
    Widget message use case with status hints from infrastructure.
    Status hints show what the system is doing (RAG search, tool calls, etc.)
    """
    
    def __init__(
        self,
        message_repository: IMessageRepository,
        chat_repository: IChatRepository,
        client_repository: IClientRepository,
        widget_session_repository: IWidgetSessionRepository,
        rag_service: IRAGService,
        chat_title_service: IChatTitleService
    ):
        self.message_repository = message_repository
        self.chat_repository = chat_repository
        self.client_repository = client_repository
        self.widget_session_repository = widget_session_repository
        self.rag_service = rag_service
        self.chat_title_service = chat_title_service

    async def execute_stream(
        self,
        session_token: str,
        chat_id: str,
        content: str,
        end_user_ip: str,
        auth_token: str = None,
        is_follow_up: bool = False
    ) -> AsyncIterator[str]:
        """
        Stream widget message response with status hints.
        Status hints come from infrastructure layer (RAG/tools).
        """
        # Validate session
        session = self.widget_session_repository.get_by_token(session_token)
        if not session or session.expires_at < datetime.now(timezone.utc):
            raise ValueError("Invalid or expired session")
        
        if session.end_user_ip != end_user_ip:
            raise ValueError("Unauthorized access")
        
        # Validate chat
        chat = self.chat_repository.get_by_id(chat_id)
        if not chat:
            raise ValueError("Chat not found")
        
        if chat.ip_address != end_user_ip:
            raise ValueError("Unauthorized access to chat")
        
        # Get client
        client = self.client_repository.get_by_id(chat.client_ip)
        if client is None:
            raise ValueError("Client not found")
        
        # Get chat history and save user message
        chat_history = self.message_repository.get_chat_history(chat.chat_id, limit=20)
        is_first_message = len(chat_history) == 0
        
        if not is_follow_up:
            now = datetime.now(timezone.utc)
            user_message_entity = Message(
                message_id=str(uuid.uuid4()),
                chat_id=chat.chat_id,
                content=content,
                ai_generated=False,
                created_at=now,
                updated_at=now
            )
            self.message_repository.create(user_message_entity)
        
        # Stream response - infrastructure will yield status hints
        full_response = ""
        async for chunk in self.rag_service.query_stream(
            question=content,
            company_name=client.client_name,
            chat_history=chat_history,
            tools=client.tools,
            auth_token=auth_token,
            system_prompt=client.system_prompt or "",
            is_follow_up=is_follow_up
        ):
            # Parse and pass through all events from infrastructure
            try:
                data = json.loads(chunk)
                chunk_type = data.get("type")
                
                if chunk_type == "status_hint":
                    # Status hint from infrastructure - pass through immediately
                    yield chunk
                    
                elif chunk_type == "content":
                    # Actual content - accumulate and pass through
                    content_data = data.get("data", "")
                    full_response += content_data
                    yield chunk
                    
                else:
                    # Other events - pass through
                    yield chunk
                    
            except json.JSONDecodeError:
                # Backward compatibility - treat as plain content
                full_response += chunk
                yield json.dumps({"type": "content", "data": chunk})
        
        # Generate title if first message
        if is_first_message:
            try:
                title = await self.chat_title_service.generate_title(content)
                chat.title = title
                self.chat_repository.update(chat)
                yield json.dumps({"type": "title_updated", "title": title})
            except Exception as e:
                pass
        
        # Save AI message
        ai_message_entity = Message(
            message_id=str(uuid.uuid4()),
            chat_id=chat.chat_id,
            content=full_response,
            ai_generated=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.message_repository.create(ai_message_entity)
        
        # Send completion
        yield json.dumps({"type": "complete"})