from repositories.message_repository import MessageRepository
from repositories.chat_repository import ChatRepository
from sqlalchemy.orm import Session


class GetChatMessagesUseCase:
    def __init__(self, db: Session):
        self.message_repository = MessageRepository(db)
        self.chat_repository = ChatRepository(db)

    def execute(self, chat_id: str) -> list:
        """Get all messages for a chat"""
        # Verify chat exists
        chat = self.chat_repository.get_by_id(chat_id)
        if not chat:
            raise ValueError(f"Chat with ID {chat_id} not found")
        
        # Get messages
        messages = self.message_repository.get_by_chat_id(chat_id)
        
        return [
            {
                "message_id": message.message_id,
                "chat_id": message.chat_id,
                "content": message.message_content,
                "ai_generated": message.ai_generated,
                "created_at": message.created_at.isoformat() if message.created_at else None
            }
            for message in messages
        ]

