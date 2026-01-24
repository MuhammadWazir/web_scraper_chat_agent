from datetime import datetime, timedelta, timezone
import uuid
from src.domain.entities.widget_session import WidgetSession
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository


class GenerateWidgetUrlUseCase:
    
    def __init__(
        self,
        widget_session_repository: IWidgetSessionRepository,
        client_repository: IClientRepository
    ):
        self.widget_session_repository = widget_session_repository
        self.client_repository = client_repository
    
    def execute(self, client_ip: str, validity_hours: int = 24) -> str:
        client = self.client_repository.get_by_id(client_ip)
        if client is None:
            raise ValueError(f"Client with IP {client_ip} not found")
        
        now = datetime.now(timezone.utc)
        widget_session = WidgetSession(
            session_token=str(uuid.uuid4()),
            client_ip=client_ip,
            end_user_ip=None,
            expires_at=now + timedelta(hours=validity_hours),
            created_at=now
        )
        
        created_session = self.widget_session_repository.create(widget_session)
        
        return created_session.session_token
