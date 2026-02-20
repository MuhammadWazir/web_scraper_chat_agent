from typing import List, Dict, Optional, AsyncIterator
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from src.configs.config import load_settings
from src.domain.abstractions.clients.abstract_llm_client import AbstractLLMClient
from src.domain.utils.chat_formatter import format_chat_history

from src.infrastructure.chains import RetrievalChain, AgentRunnable, RouterChain


class LLMClient(AbstractLLMClient):
    def __init__(self):
        settings = load_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-5-mini"
        self.default_embedding_model = "text-embedding-3-small"
        # FIX #8: Build ChatOpenAI once and reuse it — avoids object reconstruction per message
        self._chat_model = ChatOpenAI(
            model=self.default_model,
            api_key=settings.openai_api_key,
        )

    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ):
        params = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        if max_tokens is not None:
            params["max_completion_tokens"] = max_tokens
        
        response = await self.client.chat.completions.create(**params)
        return response

    async def create_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        params = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        if max_tokens is not None:
            params["max_completion_tokens"] = max_tokens

        stream = await self.client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def create_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        response = await self.client.embeddings.create(
            model=model or self.default_embedding_model,
            input=text
        )
        return response.data[0].embedding

    async def create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        response = await self.client.embeddings.create(
            model=model or self.default_embedding_model,
            input=texts
        )
        return [item.embedding for item in response.data]

    async def summarize_chunks_in_parallel(
        self,
        chunks: List[str],
        model: Optional[str] = None
    ) -> str:
        import asyncio
        
        # Limit concurrency to 5 requests at a time to avoid overwhelming the network/server
        semaphore = asyncio.Semaphore(5)
        
        async def summarize_chunk(chunk: str, index: int) -> tuple[str, str]:
            async with semaphore:
                system_message = "You are an expert summarizer. Summarize the following text into a maximum of 100 words with the most important information. use the context provided to create the complete output."
                response = await self.create_completion(
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": chunk}
                    ],
                    model=model or self.default_model
                )
                return (str(index), response.choices[0].message.content.strip())
        
        tasks = [summarize_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        results = await asyncio.gather(*tasks)
        summaries = [result[1] for result in results]
        return "\\n".join(summaries)

    def create_chain(
        self,
        retriever,
        chat_history: Optional[List[Dict[str, str]]] = None,
        company_name: str = "",
        tools: Optional[List[Dict]] = None,
        system_prompt: str = ""
    ):
        history_text = format_chat_history(chat_history) if chat_history else ""
        company_context = f"You are a representative of {company_name}. " if company_name else ""

        # FIX #8: Reuse the cached ChatOpenAI instance instead of building a new one per call
        escaped_history = history_text.replace("{", "{{").replace("}", "}}")
        escaped_company_context = company_context.replace("{", "{{").replace("}", "}}")

        prompt_parts = [escaped_company_context]

        if system_prompt:
            escaped_system_prompt = system_prompt.replace("{", "{{").replace("}", "}}")
            prompt_parts.append(escaped_system_prompt)

        prompt_parts.extend([
            "Use the following context to answer the question. "
            "If you don't know, say you don't know.\\n\\n",
            f"{escaped_history}\\n",
            "Context:\\n{context}\\n\\n",
            "Question:\\n{input}\\n\\n",
            "Helpful Answer:"
        ])

        prompt_template = "".join(prompt_parts)

        prompt = ChatPromptTemplate.from_template(prompt_template)

        document_chain = create_stuff_documents_chain(
            llm=self._chat_model,
            prompt=prompt
        )

        qa_chain = RetrievalChain(
            retriever=retriever,
            document_chain=document_chain
        )

        if not tools:
            return qa_chain

        agent_chain = AgentRunnable(
            client=self.client,
            retriever=retriever,
            tools_config=tools,
            chat_history=chat_history,
            company_name=company_name,
            system_prompt=system_prompt,
            model=self.default_model
        )

        return RouterChain(
            retriever=retriever,
            qa_chain=qa_chain,
            agent_chain=agent_chain,
            router_llm=self
        )