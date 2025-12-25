from repositories.message_repository import MessageRepository
from repositories.chat_repository import ChatRepository
from services.rag_pipeline_service import RAGPipeline
from dtos.send_message_dto import SendMessageDTO
from sqlalchemy.orm import Session


class SendMessageUseCase:
    def __init__(self, db: Session):
        self.message_repository = MessageRepository(db)
        self.chat_repository = ChatRepository(db)
        self.rag_pipeline = RAGPipeline()

    async def execute(self, dto: SendMessageDTO):
        """Send a message in a chat and get AI response using RAG"""
        # Verify chat exists
        chat = self.chat_repository.get_by_id(dto.chat_id)
        if not chat:
            raise ValueError(f"Chat with ID {dto.chat_id} not found")
        
        # Get client name from chat
        client_name = chat.client.client_name
        
        # Save user message
        user_message = self.message_repository.create(
            chat_id=dto.chat_id,
            message_content=dto.message,
            ai_generated=False
        )
        
        # Query RAG pipeline
        response = await self.rag_pipeline.query(dto.message, client_name)
        
        # Save AI response
        ai_message = self.message_repository.create(
            chat_id=dto.chat_id,
            message_content=response,
            ai_generated=True
        )
        
        return {
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

