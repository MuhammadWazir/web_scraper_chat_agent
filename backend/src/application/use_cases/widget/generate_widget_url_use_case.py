import secrets
from src.application.utils.api_key_utils import hash_api_key
from datetime import datetime, timedelta, timezone
from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository
from src.domain.abstractions.repositories.client_repository import IClientRepository
from src.domain.entities.widget_session import WidgetSession

class GenerateWidgetUrlUseCase:
    def __init__(self, widget_session_repository: IWidgetSessionRepository, client_repository: IClientRepository):
        self.widget_session_repository = widget_session_repository
        self.client_repository = client_repository

    def execute(self, api_key: str) -> str:
        # Verify client exists
        hashed_key = hash_api_key(api_key)
        client = self.client_repository.get_by_api_key_hash(hashed_key)
        if not client:
            raise ValueError("Invalid API Key")

        # Generate token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Create session
        session = WidgetSession(
            session_token=token,
            client_id=client.client_id,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc)
        )
        
        self.widget_session_repository.create(session)
        
        return token
