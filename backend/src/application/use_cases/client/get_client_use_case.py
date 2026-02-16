from src.domain.abstractions.repositories.client_repository import IClientRepository


class GetClientUseCase:
    def __init__(self, client_repository: IClientRepository):
        self.client_repository = client_repository
    
    def execute(self, client_id: str):
        client = self.client_repository.get_by_id(client_id)
        if client is None:
            raise ValueError(f"Client with ID {client_id} not found")
        return client
