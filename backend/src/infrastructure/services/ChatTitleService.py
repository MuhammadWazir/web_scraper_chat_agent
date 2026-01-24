"""Chat title service implementation"""
from src.domain.abstractions.services.chat_title_service import IChatTitleService
from src.infrastructure.clients.llm_client import LLMClient


class ChatTitleService(IChatTitleService):
    """Concrete implementation of chat title generation service"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def generate_title(self, first_message: str) -> str:
        """Generate a short title (max 20 chars) from the first message"""
        response = await self.llm_client.create_completion(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Generate a short, descriptive title (maximum 20 characters) for a chat conversation based on the first message. Return only the title, nothing else."
                },
                {
                    "role": "user",
                    "content": first_message
                }
            ]
        )
        
        title = response.choices[0].message.content.strip()
        return title

