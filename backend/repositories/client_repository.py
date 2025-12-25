from sqlalchemy.orm import Session
from models.client import Client
from typing import Optional, List
import uuid


class ClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, client_name: str, client_url: str) -> Client:
        """Create a new client"""
        client_id = str(uuid.uuid4())
        client = Client(
            client_id=client_id,
            client_name=client_name,
            client_url=client_url
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def get_by_id(self, client_id: str) -> Optional[Client]:
        """Get client by ID"""
        return self.db.query(Client).filter(Client.client_id == client_id).first()

    def get_by_name(self, client_name: str) -> Optional[Client]:
        """Get client by name"""
        return self.db.query(Client).filter(Client.client_name == client_name).first()

    def get_all(self) -> List[Client]:
        """Get all clients"""
        return self.db.query(Client).all()

    def update(self, client: Client) -> Client:
        """Update a client"""
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete(self, client_id: str) -> bool:
        """Delete a client"""
        client = self.get_by_id(client_id)
        if client:
            self.db.delete(client)
            self.db.commit()
            return True
        return False

