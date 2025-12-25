from repositories.chat_repository import ChatRepository
from sqlalchemy.orm import Session


class DeleteChatUseCase:
    def __init__(self, db: Session):
        self.chat_repository = ChatRepository(db)

    def execute(self, chat_id: str) -> bool:
        """Delete a chat"""
        return self.chat_repository.delete(chat_id)

