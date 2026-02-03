from src.domain.abstractions.repositories.message_repository import IMessageRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.abstractions.services.rag_service import IRAGService
from src.domain.abstractions.services.chat_title_service import IChatTitleService
from src.application.dtos.requests.send_message_request import SendMessageRequest
from src.domain.entities.message import Message
from src.domain.entities.chat import Chat
from typing import Dict, Any
from datetime import datetime, timezone
import uuid
import json


class SendMessageUseCase:
    """
    Use case for sending a message and getting AI response.
    Passes through status hints from infrastructure layer.
    """
    
    def __init__(
        self,
        message_repository: IMessageRepository,
        chat_repository: IChatRepository,
        client_repository: IClientRepository,
        rag_service: IRAGService,
        chat_title_service: IChatTitleService
    ):
        self.message_repository = message_repository
        self.chat_repository = chat_repository
        self.client_repository = client_repository
        self.rag_service = rag_service
        self.chat_title_service = chat_title_service

    async def execute_stream(self, request: SendMessageRequest, ip_address: str, is_follow_up: bool = False):
        """
        Stream the AI response with status hints from infrastructure.
        Status hints show what the system is doing (RAG search, tool calls, etc.)
        """
        client = self.client_repository.get_by_id(request.client_id)
        if client is None:
            raise ValueError(f"Client with ID {request.client_id} not found")
        
        # Get or create chat
        if request.chat_id:
            chat = self.chat_repository.get_by_id(request.chat_id)
            if chat is None:
                raise ValueError(f"Chat with ID {request.chat_id} not found")
            if chat.ip_address != ip_address:
                raise ValueError("Unauthorized access to chat")
        else:
            now = datetime.now(timezone.utc)
            chat = Chat(
                chat_id=str(uuid.uuid4()),
                client_ip=request.client_id,
                ip_address=ip_address,
                title=None,
                created_at=now,
                updated_at=now
            )
            chat = self.chat_repository.create(chat)
            # Send chat metadata to frontend
            yield json.dumps({"type": "chat_created", "chat_id": chat.chat_id})
        
        # Get chat history and create user message
        chat_history = self.message_repository.get_chat_history(chat.chat_id, limit=20)
        is_first_message = len(chat_history) == 0
        
        now = datetime.now(timezone.utc)
        if not is_follow_up:
            user_message_entity = Message(
                message_id=str(uuid.uuid4()),
                chat_id=chat.chat_id,
                content=request.message,
                ai_generated=False,
                created_at=now, 
                updated_at=now
            )
            user_message = self.message_repository.create(user_message_entity)
        
        # Stream the AI response
        # The RAG service will yield status hints BEFORE operations
        # Just pass them through to the frontend
        full_response = ""
        async for chunk in self.rag_service.query_stream(
            question=request.message,
            company_name=client.client_name,
            chat_history=chat_history,
            is_follow_up=is_follow_up
        ):
            # Parse the chunk to determine its type
            try:
                data = json.loads(chunk)
                chunk_type = data.get("type")
                
                if chunk_type == "status_hint":
                    # Status hint from infrastructure - pass through immediately
                    yield chunk
                    
                elif chunk_type == "content":
                    # Actual content chunk - accumulate and pass through
                    content_data = data.get("data", "")
                    full_response += content_data
                    yield chunk
                    
                else:
                    # Unknown type, pass through
                    yield chunk
                    
            except json.JSONDecodeError:
                # Not JSON, treat as plain content (backward compatibility)
                full_response += chunk
                yield json.dumps({"type": "content", "data": chunk})
        
        # Generate chat title if this is the first message
        if is_first_message:
            try:
                title = await self.chat_title_service.generate_title(request.message)
                chat.title = title
                self.chat_repository.update(chat)
                yield json.dumps({"type": "title_updated", "title": title})
            except Exception as e:
                raise e
        
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
        
        # Send completion signal
        yield json.dumps({"type": "complete"})