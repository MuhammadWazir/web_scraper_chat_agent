from repositories.message_repository import MessageRepository
from repositories.chat_repository import ChatRepository
from repositories.client_repository import ClientRepository
from services.rag_pipeline_service import RAGPipeline
from services.chat_title_service import ChatTitleService
from dtos.send_message_dto import SendMessageDTO
from sqlalchemy.orm import Session


class SendMessageUseCase:
    def __init__(self, db: Session):
        self.message_repository = MessageRepository(db)
        self.chat_repository = ChatRepository(db)
        self.client_repository = ClientRepository(db)
        self.rag_pipeline = RAGPipeline()

    async def execute(self, dto: SendMessageDTO, ip_address: str = "unknown"):
        """Send a message in a chat and get AI response using RAG. Creates chat if it doesn't exist."""
        # Get or create chat
        if dto.chat_id:
            chat = self.chat_repository.get_by_id(dto.chat_id)
            if not chat:
                raise ValueError(f"Chat with ID {dto.chat_id} not found")
        else:
            # Create new chat - will generate title after first message
            client = self.client_repository.get_by_id(dto.client_id)
            if not client:
                raise ValueError(f"Client with ID {dto.client_id} not found")
            chat = self.chat_repository.create(
                client_id=dto.client_id,
                ip_address=ip_address,
                title=None
            )
        
        # Get client name from chat
        client_name = chat.client.client_name
        
        # Check if this is the first message (for title generation)
        existing_messages = self.message_repository.get_by_chat_id(chat.chat_id)
        is_first_message = len(existing_messages) == 0
        
        # Get last 6 messages and pair them (user, AI)
        recent_messages = self.message_repository.get_last_messages(chat.chat_id, limit=6)
        
        # Pair consecutive user-AI messages
        chat_history = []
        i = 0
        while i < len(recent_messages) - 1:
            if not recent_messages[i].ai_generated and recent_messages[i + 1].ai_generated:
                chat_history.append((
                    recent_messages[i].message_content,
                    recent_messages[i + 1].message_content
                ))
                i += 2
            else:
                i += 1
        
        # Save user message
        user_message = self.message_repository.create(
            chat_id=chat.chat_id,
            message_content=dto.message,
            ai_generated=False
        )
        
        # Generate title if this is the first message
        if is_first_message:
            title = await ChatTitleService.generate_title(dto.message)
            chat.title = title
            self.chat_repository.update(chat)
        
        # Query RAG pipeline with chat history
        response = await self.rag_pipeline.query(dto.message, client_name, chat_history=chat_history)
        
        # Save AI response
        ai_message = self.message_repository.create(
            chat_id=chat.chat_id,
            message_content=response,
            ai_generated=True
        )
        
        return {
            "chat_id": chat.chat_id,
            "chat_title": chat.title,
            "user_message": {
                "message_id": user_message.message_id,
                "content": user_message.message_content,
                "ai_generated": user_message.ai_generated,
                "created_at": user_message.created_at.isoformat() if user_message.created_at else None
            },
            "ai_message": {
                "message_id": ai_message.message_id,
                "content": ai_message.message_content,
                "ai_generated": ai_message.ai_generated,
                "created_at": ai_message.created_at.isoformat() if ai_message.created_at else None
            }
        }

