from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from src.container import Container
from src.application.use_cases.client.create_client_use_case import CreateClientUseCase
from src.application.use_cases.client.get_client_use_case import GetClientUseCase
from src.application.use_cases.client.get_all_clients_use_case import GetAllClientsUseCase
from src.application.use_cases.client.delete_client_use_case import DeleteClientUseCase
from src.application.use_cases.widget.generate_widget_url_use_case import GenerateWidgetUrlUseCase
from src.application.dtos.requests.create_client_request import CreateClientRequest
from src.application.dtos.requests.update_client_request import UpdateClientRequest
from src.application.dtos.responses.client_response import ClientResponse
from src.application.use_cases.client.update_client_use_case import UpdateClientUseCase
from src.presentation.api.dependencies import get_current_user


router = APIRouter(prefix="", tags=["clients"])

container = Container()


def get_client_ip(request: Request) -> str:
    """Extract real client IP from request headers (set by Nginx)"""
    # Check X-Forwarded-For header first (set by Nginx)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, get the first one (original client)
        return forwarded_for.split(",")[0].strip()
    
    # Fallback to X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Last resort: use direct connection IP (will be Docker IP in production)
    if request.client:
        return request.client.host
    
    return "unknown"


@router.post("/create-client", response_model=ClientResponse)
async def create_client(
    request: CreateClientRequest,
    http_request: Request,
    use_case: CreateClientUseCase = Depends(lambda: container.create_client_use_case()),
    current_user: dict = Depends(get_current_user)
):
    try:
        client_ip = get_client_ip(http_request)
        result = await use_case.execute(request, client_ip)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clients", response_model=List[ClientResponse])
async def get_all_clients(
    use_case: GetAllClientsUseCase = Depends(lambda: container.get_all_clients_use_case()),
    current_user: dict = Depends(get_current_user)
):
    clients = use_case.execute()
    return [
        ClientResponse(
            client_id=client.client_id,
            client_ip=client.client_ip,
            company_name=client.client_name,
            website_url=client.client_url,
            system_prompt=client.system_prompt,
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
            client_ip=client.client_ip,
            company_name=client.client_name,
            website_url=client.client_url,
            tools=client.tools,
            system_prompt=client.system_prompt,
            created_at=client.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    request: UpdateClientRequest,
    use_case: UpdateClientUseCase = Depends(lambda: container.update_client_use_case()),
    current_user: dict = Depends(get_current_user)
):
    try:
        return use_case.execute(client_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clients/{client_id}")
async def delete_client(
    client_id: str,
    use_case: DeleteClientUseCase = Depends(lambda: container.delete_client_use_case()),
    current_user: dict = Depends(get_current_user)
):
    """Delete a client and their associated Qdrant collection"""
    try:
        success = use_case.execute(client_id)
        return {"success": success, "message": f"Client {client_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
