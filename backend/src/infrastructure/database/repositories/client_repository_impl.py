from sqlalchemy.orm import Session
from typing import Optional, List

from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.entities.client import Client
from src.infrastructure.database.models.client_model import ClientModel


class ClientRepositoryImpl(IClientRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: ClientModel) -> Client:
        return Client(
            client_ip=model.client_ip,
            client_name=model.client_name,
            client_url=model.client_url,
            api_key_hash=model.api_key_hash,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: Client) -> ClientModel:
        return ClientModel(
            client_ip=entity.client_ip,
            client_name=entity.client_name,
            client_url=entity.client_url,
            api_key_hash=entity.api_key_hash,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def create(self, client_ip: str, client_name: str, client_url: str, api_key_hash: Optional[str] = None) -> Client:
        model = ClientModel(
            client_ip=client_ip,
            client_name=client_name,
            client_url=client_url,
            api_key_hash=api_key_hash
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, client_ip: str) -> Optional[Client]:
        model = self.db.query(ClientModel).filter(ClientModel.client_ip == client_ip).first()
        return self._to_entity(model) if model else None
    
    def get_by_name(self, client_name: str) -> Optional[Client]:
        model = self.db.query(ClientModel).filter(ClientModel.client_name == client_name).first()
        return self._to_entity(model) if model else None
    
    def get_all(self) -> List[Client]:
        models = self.db.query(ClientModel).all()
        return [self._to_entity(model) for model in models]
    
    def update(self, client: Client) -> Client:
        model = self.db.query(ClientModel).filter(ClientModel.client_ip == client.client_ip).first()
        if model:
            model.client_name = client.client_name
            model.client_url = client.client_url
            model.updated_at = client.updated_at
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        raise ValueError(f"Client with IP {client.client_ip} not found")
    
    def delete(self, client_ip: str) -> bool:
        model = self.db.query(ClientModel).filter(ClientModel.client_ip == client_ip).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False
