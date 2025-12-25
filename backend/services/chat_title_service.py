from helpers.ai_client_helper import get_openai_client


class ChatTitleService:
    @staticmethod
    async def generate_title(first_message: str) -> str:
        """Generate a short title (max 60 chars) from the first message"""
        client = await get_openai_client()
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Generate a short, descriptive title (maximum 20 characters) for a chat conversation based on the first message. Return only the title, nothing else."
                },
                {
                    "role": "user",
                    "content": first_message
                }
            ],
            temperature=0.7,
            max_tokens=20
        )
        
        title = response.choices[0].message.content.strip()
        return title

