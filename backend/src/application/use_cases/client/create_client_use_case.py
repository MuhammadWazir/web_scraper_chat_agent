from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.abstractions.services.rag_service import IRAGService
from src.application.dtos.requests.create_client_request import CreateClientRequest
from src.application.dtos.responses.client_response import ClientResponse
from src.application.utils.api_key_utils import generate_api_key, hash_api_key


class CreateClientUseCase:
    
    def __init__(self, client_repository: IClientRepository, rag_service: IRAGService):
        self.client_repository = client_repository
        self.rag_service = rag_service

    async def execute(self, request: CreateClientRequest, client_ip: str) -> ClientResponse:
        await self.rag_service.build(request.website_url, request.company_name)
        
        # Generate API key
        api_key = generate_api_key()
        api_key_hash = hash_api_key(api_key)
        
        # Create client in database (client_id will be auto-generated as UUID)
        client = self.client_repository.create(
            client_ip=client_ip,
            client_name=request.company_name,
            client_url=request.website_url,
            api_key_hash=api_key_hash
        )
        return ClientResponse(
            client_id=client.client_id,
            client_ip=client.client_ip,
            company_name=client.client_name,
            website_url=client.client_url,
            api_key=api_key,
            created_at=client.created_at
        )
