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
    
    def execute(self, client_id: str, validity_hours: int = 24) -> str:
        # Verify client exists
        client = self.client_repository.get_by_id(client_id)
        if client is None:
            raise ValueError(f"Client with ID {client_id} not found")
        
        # Create new widget session
        widget_session = WidgetSession.create_new(
            client_id=client_id,
            validity_hours=validity_hours
        )
        
        # Save to database
        created_session = self.widget_session_repository.create(widget_session)
        
        return created_session.session_token
