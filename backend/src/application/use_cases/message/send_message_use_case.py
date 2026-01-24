from src.domain.abstractions.repositories.message_repository import IMessageRepository
from src.domain.abstractions.repositories.chat_repository import IChatRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.abstractions.services.rag_service import IRAGService
from src.domain.abstractions.services.chat_title_service import IChatTitleService
from src.application.dtos.requests.send_message_request import SendMessageRequest
from src.domain.entities.message import Message
from typing import Dict, Any
from datetime import datetime, timezone
import uuid


class SendMessageUseCase:
    """Use case for sending a message and getting AI response"""
    
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

    async def execute(self, request: SendMessageRequest, ip_address: str = "unknown") -> Dict[str, Any]:
        """Send a message in a chat and get AI response using RAG. Creates chat if it doesn't exist."""
        # Get or create chat
        if request.chat_id:
            chat = self.chat_repository.get_by_id(request.chat_id)
            if not chat:
                raise ValueError(f"Chat with ID {request.chat_id} not found")
        else:
            # Create new chat - will generate title after first message
            client = self.client_repository.get_by_id(request.client_id)
            if not client:
                raise ValueError(f"Client with ID {request.client_id} not found")
            chat = self.chat_repository.create(
                client_id=request.client_id,
                ip_address=ip_address,
                title=None
            )
        
        # Get client for RAG query
        client = self.client_repository.get_by_id(chat.client_ip)
        if not client:
            raise ValueError(f"Client with ID {chat.client_ip} not found")
        
        # Check if this is the first message (for title generation)
        existing_messages = self.message_repository.get_by_chat_id(chat.chat_id)
        is_first_message = len(existing_messages) == 0
        
        # Get recent messages for chat history (last 6 messages)
        recent_messages = existing_messages[-6:] if len(existing_messages) >= 6 else existing_messages
        
        # Pair consecutive user-AI messages for chat history
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
        
        # Save user message
        now = datetime.now(timezone.utc)
        user_message_entity = Message(
            message_id=str(uuid.uuid4()),
            chat_id=chat.chat_id,
            content=request.message,
            ai_generated=False,
            created_at=now,
            updated_at=now
        )
        user_message = self.message_repository.create(user_message_entity)
        
        # Generate title if this is the first message
        if is_first_message:
            title = await self.chat_title_service.generate_title(request.message)
            chat = chat.model_copy(update={"title": title, "updated_at": datetime.now(timezone.utc)})
            self.chat_repository.update(chat)
        
        # Query RAG pipeline with chat history
        response = await self.rag_service.query(request.message, client.client_name, chat_history=chat_history)
        
        # Save AI response
        ai_message_entity = Message(
            message_id=str(uuid.uuid4()),
            chat_id=chat.chat_id,
            content=response,
            ai_generated=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        ai_message = self.message_repository.create(ai_message_entity)
        
        return {
            "chat_id": chat.chat_id,
            "chat_title": chat.title,
            "user_message": {
                "message_id": user_message.message_id,
                "content": user_message.content,
                "ai_generated": user_message.ai_generated,
                "created_at": user_message.created_at.isoformat() if user_message.created_at else None
            },
            "ai_message": {
                "message_id": ai_message.message_id,
                "content": ai_message.content,
                "ai_generated": ai_message.ai_generated,
                "created_at": ai_message.created_at.isoformat() if ai_message.created_at else None
            }
        }