from repositories.message_repository import MessageRepository
from repositories.chat_repository import ChatRepository
from services.rag_pipeline_service import RAGPipeline
from dtos.query_client_dto import QueryClientDTO
from sqlalchemy.orm import Session


class QueryClientUseCase:
    def __init__(self, db: Session):
        self.message_repository = MessageRepository(db)
        self.chat_repository = ChatRepository(db)
        self.rag_pipeline = RAGPipeline()

    async def execute(self, dto: QueryClientDTO, chat_id: str, ip_address: str):
        """Query the RAG pipeline and save messages"""
        # Query using RAG pipeline
        response = await self.rag_pipeline.query(dto.question, dto.company_name)
        
        # Save user message
        user_message = self.message_repository.create(
            chat_id=chat_id,
            message_content=dto.question,
            ai_generated=False
        )
        
        # Save AI response
        ai_message = self.message_repository.create(
            chat_id=chat_id,
            message_content=response,
            ai_generated=True
        )
        
        return {
            "response": response,
            "user_message_id": user_message.message_id,
            "ai_message_id": ai_message.message_id
        }

