from src.domain.abstractions.repositories.client_repository import IClientRepository


class GetClientUseCase:
    def __init__(self, client_repository: IClientRepository):
        self.client_repository = client_repository
    
    def execute(self, client_ip: str):
        client = self.client_repository.get_by_id(client_ip)
        if client is None:
            raise ValueError(f"Client with IP {client_ip} not found")
        return client
