import asyncio
from openai import AsyncOpenAI
from configs.config import load_settings

config = load_settings()

# Global client for connection pooling to support concurrent requests
_openai_client = None

async def get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=config.openai_api_key)
    return _openai_client

async def summarize_chunks_in_parallel(chunks: list[str], model: str = "gpt-4o") -> str:
    client = await get_openai_client()
    
    async def summarize_chunk(chunk: str, index: int) -> tuple[str, str]:
        system_message = "You are an expert summarizer. Summarize the following text into a maximum of 100 words with the most important information. use the context provided to create the complete output."
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": chunk}
            ],
        )
        return (str(index), response.choices[0].message.content.strip())
    
    tasks = [summarize_chunk(chunk, i) for i, chunk in enumerate(chunks)]
    results = await asyncio.gather(*tasks)
    summaries = [result[1] for result in results]
    return "\n".join(summaries)

