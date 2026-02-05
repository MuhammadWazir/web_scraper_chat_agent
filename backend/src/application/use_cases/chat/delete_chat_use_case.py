"""Delete chat use case - with dependency injection"""
from src.domain.abstractions.repositories.chat_repository import IChatRepository


class DeleteChatUseCase:
    """Use case for deleting a chat"""
    
    def __init__(self, chat_repository: IChatRepository):
        self.chat_repository = chat_repository

    def execute(self, chat_id: str) -> bool:
        """Delete a chat by ID"""
        return self.chat_repository.delete(chat_id)
