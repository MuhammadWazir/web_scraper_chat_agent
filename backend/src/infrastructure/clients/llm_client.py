"""OpenAI LLM client implementation"""
from typing import List, Dict, Optional, AsyncIterator, Any, Tuple
from src.domain.utils.chat_formatter import format_chat_history_tuples
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from src.configs.config import load_settings
from src.domain.abstractions.clients.abstract_llm_client import AbstractLLMClient


class LLMClient(AbstractLLMClient):
    """OpenAI implementation of LLM client"""
    
    def __init__(self):
        settings = load_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-5-mini"
        self.default_embedding_model = "text-embedding-3-small"

    async def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Any:
        params = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
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
        
        # Only include max_tokens if it has a value
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
        stream = await self.client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def create_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Create an embedding for text"""
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
        """Create embeddings for multiple texts"""
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
        """Summarize multiple chunks in parallel"""
        import asyncio
        
        async def summarize_chunk(chunk: str, index: int) -> tuple[str, str]:
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
        return "\n".join(summaries)

    def _format_chat_history(self, chat_history: List[Tuple[str, str]]) -> str:
        """Format chat history as a conversation string"""
        return format_chat_history_tuples(chat_history)

    def create_chain(
        self,
        retriever,
        chat_history: Optional[List[Tuple[str, str]]] = None,
        company_name: str = ""
    ) -> RetrievalQA:
        """Create a QA chain with optional chat history context"""
        chat_history_context = self._format_chat_history(chat_history) if chat_history else ""
        company_context = f"You are a representative of {company_name}. " if company_name else ""
        prompt_template = f"""{company_context}Use the following pieces of context to answer the question at the end. 
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
{chat_history_context}
Context: {{context}}

Question: {{question}}
Helpful Answer:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        settings = load_settings()
        model = ChatOpenAI(
            model="gpt-5-mini",
            api_key=settings.openai_api_key
        )

        return RetrievalQA.from_chain_type(
            llm=model,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt}
        )
