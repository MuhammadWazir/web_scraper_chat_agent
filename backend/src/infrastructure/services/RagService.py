from typing import List, Dict, AsyncIterator, Optional
import asyncio
from langchain.schema import BaseRetriever, Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from src.domain.abstractions.services.rag_service import IRAGService
from src.infrastructure.services.WebsiteLoader import WebsiteLoaderService
from src.infrastructure.services.DocumentChunker import DocumentChunkingService
from src.infrastructure.services.EmbeddingService import EmbeddingService
from src.infrastructure.services.VectorStore import VectorStoreService
from src.infrastructure.clients.llm_client import LLMClient
from src.infrastructure.clients.vector_store_client import VectorStoreClient
from src.infrastructure.chains.agent_chain import AgentRunnable
from src.domain.utils.chat_formatter import format_chat_history
import json


class QdrantRetriever(BaseRetriever):
    vector_store: VectorStoreService
    collection_name: str
    k: int = 3

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        results = self.vector_store.search(query, self.collection_name, k=self.k)
        return [Document(page_content=result.text, metadata=result.metadata) for result in results]

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_relevant_documents, query)


class RAGService(IRAGService):
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store_client: VectorStoreClient,
    ):
        self.loader = None
        self.chunker = DocumentChunkingService()
        self.embeddings = embedding_service
        self.llm_client = LLMClient()
        self.vector_store_service = VectorStoreService(
            self.embeddings.get_embeddings(),
            vector_store_client,
        )
        self.company_name = None

    async def build(self, url: str, company_name: str) -> None:
        self.loader = WebsiteLoaderService(url)
        self.company_name = company_name
        documents = await self.loader.scrape_website(url)
        chunks = self.chunker.create_chunks(documents)
        self.vector_store_service.create_store(documents=chunks, collection_name=company_name)

    async def query(
        self,
        question: str,
        company_name: str,
        chat_history: List[Dict[str, str]] = None,
        tools: List[Dict] = None,
        auth_token: str = None
    ) -> str:
        retriever = QdrantRetriever(
            vector_store=self.vector_store_service,
            collection_name=company_name,
            k=3
        )

        qa_chain = self.llm_client.create_chain(
            retriever,
            chat_history=chat_history,
            company_name=company_name,
            tools=tools
        )

        try:
            if tools:
                result = await qa_chain.ainvoke(
                    {"input": question, "chat_history": chat_history or []},
                    config={"configurable": {"auth_token": auth_token}}
                )
            else:
                result = await qa_chain.ainvoke(question)

            if isinstance(result, dict):
                answer = result.get("result", result.get("output", str(result)))
                final_answer = str(answer) if answer else "I don't know."
            elif isinstance(result, str):
                final_answer = result
            else:
                final_answer = str(result)

            return final_answer

        except Exception as e:
            raise

    async def query_stream(
        self,
        question: str,
        company_name: str,
        chat_history: List[Dict[str, str]] = None,
        tools: Optional[List[Dict]] = None,
        auth_token: Optional[str] = None,
        system_prompt: Optional[str] = "",
        is_follow_up: bool = False
    ) -> AsyncIterator[str]:
        """
        Stream response with status hints before each major operation.
        Yields status hints BEFORE the operation starts, not after.

        IMPORTANT: If tools are provided (agentic tool calls), skip RAG query
        and let the agent decide when to use tools. Only query vector DB
        when no tools are provided (simple Q&A without tool use).
        """

        retriever = QdrantRetriever(
            vector_store=self.vector_store_service,
            collection_name=company_name,
            k=3
        )

        # If tools are provided (agentic mode), skip RouterChain and go straight to
        # AgentRunnable. RouterChain adds a redundant extra LLM call just to decide
        # whether to use tools — AgentRunnable already does this via tool_choice='auto'
        # in the same call as the response, saving a full LLM round-trip.
        if tools:
            # Combine system prompt with follow-up instruction if needed
            effective_system_prompt = system_prompt or ""
            if is_follow_up:
                follow_up_instr = "The user has been inactive for 3 minutes. Send a very brief, friendly follow-up message to see if they need more help. Just one short sentence."
                effective_system_prompt = f"{effective_system_prompt}\n\n{follow_up_instr}" if effective_system_prompt else follow_up_instr

            # Build the retriever for context (AgentRunnable uses it internally)
            agent = AgentRunnable(
                client=self.llm_client.client,
                retriever=retriever,
                tools_config=tools,
                chat_history=chat_history,
                company_name=company_name,
                system_prompt=effective_system_prompt,
                model=self.llm_client.default_model
            )

            async for chunk in agent.astream(
                {"input": question, "chat_history": chat_history or []},
                config={"configurable": {"auth_token": auth_token}}
            ):
                yield chunk
            return

        # HINT #1: About to search knowledge base (only for non-tool queries)
        yield json.dumps({
            "type": "status_hint",
            "message": f"🔍 Searching {company_name}'s knowledge base..."
        })

        # Only query RAG when NO tools are provided
        docs = await retriever.ainvoke(question)
        context = "\n\n".join(d.page_content for d in docs)

        # Prepare the prompt
        history = format_chat_history(chat_history) if chat_history else ""
        company_context = f"You are a representative of {company_name}. " if company_name else ""

        prompt_parts = [company_context]
        if system_prompt:
            prompt_parts.append(system_prompt)

        if auth_token:
            prompt_parts.append(f"API token: {auth_token}")

        if is_follow_up:
            prompt_parts.append("The user has been inactive for 3 minutes. Send a very brief, friendly follow-up message to see if they need more help. Just one short sentence.")

        prompt_parts.append(f"Context:\n{context}")
        if history:
            prompt_parts.append(f"Chat History:\n{history}")

        full_prompt = "\n\n".join(prompt_parts)

        messages = [
            {"role": "system", "content": full_prompt},
            {"role": "user", "content": question}
        ]

        # HINT #2: About to generate response
        yield json.dumps({
            "type": "status_hint",
            "message": "💭 Generating response..."
        })

        # NOW stream the actual completion
        async for chunk in self.llm_client.create_streaming_completion(messages):
            yield json.dumps({
                "type": "content",
                "data": chunk
            })
