"""Get chat messages use case - with dependency injection"""
from src.domain.abstractions.repositories.message_repository import IMessageRepository
from src.application.dtos.responses.message_response import MessageResponse
from typing import List


class GetChatMessagesUseCase:
    """Use case for getting all messages in a chat"""
    
    def __init__(self, message_repository: IMessageRepository):
        self.message_repository = message_repository

    def execute(self, chat_id: str) -> List[MessageResponse]:
        """Get all messages for a chat"""
        messages = self.message_repository.get_by_chat_id(chat_id)
        
        return [
            MessageResponse(
                message_id=message.message_id,
                chat_id=message.chat_id,
                role=message.role,
                content=message.content,
                created_at=message.created_at
            )
            for message in messages
        ]
