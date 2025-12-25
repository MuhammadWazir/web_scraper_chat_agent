from repositories.client_repository import ClientRepository
from services.rag_pipeline_service import RAGPipeline
from dtos.create_client_dto import CreateClientDTO
from sqlalchemy.orm import Session


class CreateClientUseCase:
    def __init__(self, db: Session):
        self.client_repository = ClientRepository(db)
        self.rag_pipeline = RAGPipeline()

    async def execute(self, dto: CreateClientDTO):
        """Create a new client and build RAG pipeline"""
        # Build RAG pipeline first
        await self.rag_pipeline.build(dto.website_url, dto.company_name)
        
        # Create client in database
        client = self.client_repository.create(
            client_name=dto.company_name,
            client_url=dto.website_url
        )
        
        return {
            "client_id": client.client_id,
            "company_name": client.client_name,
            "website_url": client.client_url,
            "created_at": client.created_at.isoformat() if client.created_at else None
        }

