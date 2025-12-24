import asyncio
from openai import AsyncOpenAI
from configs.config import load_settings
from configs.constants import (
    BACKGROUND_CONTEXT_PROMPT, 
    RULES_SECTION_PROMPT,
    FAQS_SECTION_PROMPT, 
    SCRIPT_CREATION_PROMPT
)

config = load_settings()

# Global client for connection pooling to support concurrent requests
_openai_client = None

async def get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=config.openai_api_key)
    return _openai_client

async def process_prompts(website_url: str, content: str, audience: str, model: str = "gpt-4o"):
    print(f"Processing prompts for {website_url} and audience: {audience}")
    client = await get_openai_client()
    
    prompts = {
        "background": _prepare_prompt(BACKGROUND_CONTEXT_PROMPT, website_url, content, audience),
        "rules": _prepare_prompt(RULES_SECTION_PROMPT, website_url, content, audience),
        "faqs": _prepare_prompt(FAQS_SECTION_PROMPT, website_url, content, audience),
        "script": _prepare_prompt(SCRIPT_CREATION_PROMPT, website_url, content, audience)
    }
    
    tasks = [_call_openai(client, model, prompt, key) for key, prompt in prompts.items()]
    results = await asyncio.gather(*tasks)
    
    return dict(results)


def _prepare_prompt(template: str, url: str, content: str, audience: str) -> str:
    # Common replacements
    prompt = template.replace(
        "VOICE / MESSAGING  (select one, and add the website address, which extracts it all)",
        f"VOICE - {url}"
    ).replace(
        "[user input description]",
        f"Website visitor - live chat. {audience}"
    ).replace(
        "TEXT", content
    )
    
    # Rules-specific replacements
    if "TYPE OF CONVERSATION:" in prompt:
        prompt = prompt.replace(
            "**TYPE OF CONVERSATION:",
            f"**TYPE OF CONVERSATION:\nVOICE - {url}\n\n**CONVERSATION CONTEXT:"
        )
    
    # Script-specific replacements  
    if "TYPE OF CONVERSATION RIGHT NOW:" in prompt:
        prompt = prompt.replace(
            "**TYPE OF CONVERSATION RIGHT NOW:\nVOICE / MESSAGING  (select one, and add the website address, which extracts it all)",
            f"**TYPE OF CONVERSATION RIGHT NOW:\nVOICE - {url}"
        )
    
    return prompt


async def _call_openai(client: AsyncOpenAI, model: str, prompt: str, key: str):
    system_message = "You are an expert voice agent creator. Generate the requested content based on the provided website data. Do not ask for clarification - use the context provided to create the complete output. Return plain text, no markdown, no * or # or \\n or any other formatting."
    response = None
    if model == "gpt-5":
        response = await client.chat.completions.create(
                model=model,
                reasoning_effort="medium",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
            )
    else:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
        )
    return (key, response.choices[0].message.content.strip()) 

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

