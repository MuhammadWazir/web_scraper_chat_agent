"""Create client use case - with dependency injection"""
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.abstractions.services.rag_service import IRAGService
from src.application.dtos.requests.create_client_request import CreateClientRequest
from src.application.dtos.responses.client_response import ClientResponse


class CreateClientUseCase:
    """Use case for creating a new client and building RAG pipeline"""
    
    def __init__(self, client_repository: IClientRepository, rag_service: IRAGService):
        self.client_repository = client_repository
        self.rag_service = rag_service

    async def execute(self, request: CreateClientRequest) -> ClientResponse:
        """Create a new client and build RAG pipeline"""
        # Build RAG pipeline first
        await self.rag_service.build(request.website_url, request.company_name)
        
        # Create client in database
        client = self.client_repository.create(
            client_name=request.company_name,
            client_url=request.website_url
        )
        
        return ClientResponse(
            client_id=client.client_id,
            company_name=client.client_name,
            website_url=client.client_url,
            created_at=client.created_at
        )
