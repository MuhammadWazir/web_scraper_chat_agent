"""Client API routes"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from src.container import Container
from src.application.use_cases.client.create_client_use_case import CreateClientUseCase
from src.application.dtos.requests.create_client_request import CreateClientRequest
from src.application.dtos.responses.client_response import ClientResponse
from src.domain.abstractions.repositories.client_repository import IClientRepository


router = APIRouter(prefix="", tags=["clients"])

# Global container instance
container = Container()


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    if request.client:
        return request.client.host
    return "unknown"


@router.post("/create-client", response_model=ClientResponse)
async def create_client(
    request: CreateClientRequest,
    use_case: CreateClientUseCase = Depends(lambda: container.create_client_use_case())
):
    """Create a new client and build RAG pipeline"""
    try:
        result = await use_case.execute(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients", response_model=List[ClientResponse])
async def get_all_clients(
    client_repository: IClientRepository = Depends(lambda: container.client_repository())
):
    """Get all clients"""
    clients = client_repository.get_all()
    return [
        ClientResponse(
            client_id=client.client_id,
            company_name=client.client_name,
            website_url=client.client_url,
            created_at=client.created_at
        )
        for client in clients
    ]


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    client_repository: IClientRepository = Depends(lambda: container.client_repository())
):
    """Get a client by ID"""
    client = client_repository.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientResponse(
        client_id=client.client_id,
        company_name=client.client_name,
        website_url=client.client_url,
        created_at=client.created_at
    )
