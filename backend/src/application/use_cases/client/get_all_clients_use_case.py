from typing import List
from src.domain.entities.client import Client
from src.domain.abstractions.repositories.client_repository import IClientRepository


class GetAllClientsUseCase:
    def __init__(self, client_repository: IClientRepository):
        self.client_repository = client_repository
    
    def execute(self) -> List[Client]:
        return self.client_repository.get_all()
