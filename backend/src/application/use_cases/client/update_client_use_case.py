from typing import Dict, Any, Optional
from datetime import datetime
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.application.dtos.requests.update_client_request import UpdateClientRequest
from src.application.dtos.responses.client_response import ClientResponse


class UpdateClientUseCase:
    def __init__(self, client_repository: IClientRepository):
        self.client_repository = client_repository

    def execute(self, client_ip: str, request: UpdateClientRequest) -> ClientResponse:
        client = self.client_repository.get_by_id(client_ip)
        
        if client is None:
            raise ValueError(f"Client with IP {client_ip} not found")

        update_data = {}
        if request.tools is not None:
            update_data["tools"] = request.tools
        if request.system_prompt is not None:
            update_data["system_prompt"] = request.system_prompt
            
        if not update_data:
            return ClientResponse(
                client_ip=client.client_ip,
                company_name=client.client_name,
                website_url=client.client_url,
                api_key=None,
                tools=client.tools,
                system_prompt=client.system_prompt,
                created_at=client.created_at
            )

        updated_client = client.model_copy(update=update_data)
        saved_client = self.client_repository.update(updated_client)
        
        return ClientResponse(
            client_ip=saved_client.client_ip,
            company_name=saved_client.client_name,
            website_url=saved_client.client_url,
            api_key=None,
            tools=saved_client.tools,
            system_prompt=saved_client.system_prompt,
            created_at=saved_client.created_at
        )
