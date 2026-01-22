"""Client repository implementation - concrete SQLAlchemy implementation"""
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid

from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.entities.client import Client
from src.infrastructure.database.models.client_model import ClientModel


class ClientRepositoryImpl(IClientRepository):
    """Concrete implementation of IClientRepository using SQLAlchemy"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_entity(self, model: ClientModel) -> Client:
        """Convert ORM model to domain entity"""
        return Client(
            client_id=model.client_id,
            client_name=model.client_name,
            client_url=model.client_url,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _to_model(self, entity: Client) -> ClientModel:
        """Convert domain entity to ORM model"""
        return ClientModel(
            client_id=entity.client_id,
            client_name=entity.client_name,
            client_url=entity.client_url,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def create(self, client_name: str, client_url: str) -> Client:
        """Create a new client"""
        client_id = str(uuid.uuid4())
        model = ClientModel(
            client_id=client_id,
            client_name=client_name,
            client_url=client_url
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
    
    def get_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID"""
        model = self.db.query(ClientModel).filter(ClientModel.client_id == client_id).first()
        return self._to_entity(model) if model else None
    
    def get_by_name(self, client_name: str) -> Optional[Client]:
        """Get client by name"""
        model = self.db.query(ClientModel).filter(ClientModel.client_name == client_name).first()
        return self._to_entity(model) if model else None
    
    def get_all(self) -> List[Client]:
        """Get all clients"""
        models = self.db.query(ClientModel).all()
        return [self._to_entity(model) for model in models]
    
    def update(self, client: Client) -> Client:
        """Update a client"""
        model = self.db.query(ClientModel).filter(ClientModel.client_id == client.client_id).first()
        if model:
            model.client_name = client.client_name
            model.client_url = client.client_url
            model.updated_at = client.updated_at
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        raise ValueError(f"Client with ID {client.client_id} not found")
    
    def delete(self, client_id: str) -> bool:
        """Delete a client"""
        model = self.db.query(ClientModel).filter(ClientModel.client_id == client_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False
