from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from src.container import Container
from src.application.use_cases.client.create_client_use_case import CreateClientUseCase
from src.application.use_cases.client.get_client_use_case import GetClientUseCase
from src.application.use_cases.client.get_all_clients_use_case import GetAllClientsUseCase
from src.application.use_cases.widget.generate_widget_url_use_case import GenerateWidgetUrlUseCase
from src.application.dtos.requests.create_client_request import CreateClientRequest
from src.application.dtos.responses.client_response import ClientResponse
from src.presentation.utils.request_utils import get_client_ip


router = APIRouter(prefix="", tags=["clients"])

container = Container()


@router.post("/create-client", response_model=ClientResponse)
async def create_client(
    request: CreateClientRequest,
    http_request: Request,
    use_case: CreateClientUseCase = Depends(lambda: container.create_client_use_case())
):
    try:
        client_ip = get_client_ip(http_request)
        result = await use_case.execute(request, client_ip)
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
            client_ip=client.client_ip,
            company_name=client.client_name,
            website_url=client.client_url,
            created_at=client.created_at
        )
        for client in clients
    ]


@router.get("/clients/{client_ip}", response_model=ClientResponse)
async def get_client(
    client_ip: str,
    use_case: GetClientUseCase = Depends(lambda: container.get_client_use_case())
):
    try:
        client = use_case.execute(client_ip)
        return ClientResponse(
            client_ip=client.client_ip,
            company_name=client.client_name,
            website_url=client.client_url,
            created_at=client.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clients/{client_ip}/generate-widget-url")
async def generate_widget_url(
    client_ip: str,
    http_request: Request,
    use_case: GenerateWidgetUrlUseCase = Depends(lambda: container.generate_widget_url_use_case())
):
    try:
        request_ip = get_client_ip(http_request)
        
        # Verify the requesting IP matches the client_ip (basic auth)
        if request_ip != client_ip:
            raise HTTPException(status_code=403, detail="IP does not match client")
        
        session_token = use_case.execute(client_ip)
        
        return {
            "session_token": session_token,
            "client_ip": client_ip
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
