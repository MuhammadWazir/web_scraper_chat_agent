from src.domain.abstractions.repositories.widget_session_repository import IWidgetSessionRepository


class ValidateWidgetSessionUseCase:
    def __init__(self, widget_session_repository: IWidgetSessionRepository):
        self.widget_session_repository = widget_session_repository
    
    def execute(self, session_token: str, end_user_ip: str) -> bool:
        widget_session = self.widget_session_repository.get_by_token(session_token)
        
        if widget_session is None:
            return False
        
        return widget_session.validate(end_user_ip)
