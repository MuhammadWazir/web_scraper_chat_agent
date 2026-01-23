from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from src.container import Container
from src.application.use_cases.client.create_client_use_case import CreateClientUseCase
from src.application.use_cases.client.get_client_use_case import GetClientUseCase
from src.application.use_cases.client.get_all_clients_use_case import GetAllClientsUseCase
from src.application.use_cases.widget.generate_widget_url_use_case import GenerateWidgetUrlUseCase
from src.application.dtos.requests.create_client_request import CreateClientRequest
from src.application.dtos.responses.client_response import ClientResponse
from src.infrastructure.utils.request_utils import get_client_ip


router = APIRouter(prefix="", tags=["clients"])

container = Container()


@router.post("/create-client", response_model=ClientResponse)
async def create_client(
    request: CreateClientRequest,
    use_case: CreateClientUseCase = Depends(lambda: container.create_client_use_case())
):
    try:
        result = await use_case.execute(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients", response_model=List[ClientResponse])
async def get_all_clients(
    use_case: GetAllClientsUseCase = Depends(lambda: container.get_all_clients_use_case())
):
    clients = use_case.execute()
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
    use_case: GetClientUseCase = Depends(lambda: container.get_client_use_case())
):
    try:
        client = use_case.execute(client_id)
        return ClientResponse(
            client_id=client.client_id,
            company_name=client.client_name,
            website_url=client.client_url,
            created_at=client.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clients/{client_id}/generate-widget-url")
async def generate_widget_url(
    client_id: str,
    http_request: Request,
    use_case: GenerateWidgetUrlUseCase = Depends(lambda: container.generate_widget_url_use_case())
):
    try:
        client_ip = get_client_ip(http_request)
        session_token = use_case.execute(client_id)
        
        return {
            "session_token": session_token,
            "client_id": client_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
