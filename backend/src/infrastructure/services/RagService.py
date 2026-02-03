from typing import List, Dict, AsyncIterator, Optional
from langchain.schema import BaseRetriever, Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from src.domain.abstractions.services.rag_service import IRAGService
from src.infrastructure.services.WebsiteLoader import WebsiteLoaderService
from src.infrastructure.services.DocumentChunker import DocumentChunkingService
from src.infrastructure.services.EmbeddingService import EmbeddingService
from src.infrastructure.services.VectorStore import VectorStoreService
from src.infrastructure.clients.llm_client import LLMClient
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
        return self._get_relevant_documents(query, run_manager=run_manager)


class RAGService(IRAGService):
    def __init__(self):
        self.loader = None
        self.chunker = DocumentChunkingService()
        self.embeddings = EmbeddingService()
        self.llm_client = LLMClient()
        self.vector_store_service = None
        self.company_name = None

    async def build(self, url: str, company_name: str) -> None:
        self.loader = WebsiteLoaderService(url)
        self.company_name = company_name
        documents = await self.loader.scrape_website(url)
        chunks = self.chunker.create_chunks(documents)
        
        self.vector_store_service = VectorStoreService(self.embeddings.get_embeddings())
        self.vector_store_service.create_store(documents=chunks, collection_name=company_name)

    async def query(
        self,
        question: str,
        company_name: str,
        chat_history: List[Dict[str, str]] = None,
        tools: List[Dict] = None,
        auth_token: str = None
    ) -> str:
        if self.vector_store_service is None:
            self.vector_store_service = VectorStoreService(self.embeddings.get_embeddings())
        
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
        """
        
        # Initialize vector store if needed
        if self.vector_store_service is None:
            self.vector_store_service = VectorStoreService(self.embeddings.get_embeddings())
        
        # HINT #1: About to search knowledge base
        yield json.dumps({
            "type": "status_hint",
            "message": f"🔍 Searching {company_name}'s knowledge base..."
        })
        
        # NOW perform the retrieval
        retriever = QdrantRetriever(
            vector_store=self.vector_store_service,
            collection_name=company_name,
            k=3
        )
        
        docs = await retriever.ainvoke(question)
        context = "\\n\\n".join(d.page_content for d in docs)
        
        # Prepare the prompt
        history = format_chat_history(chat_history) if chat_history else ""
        company_context = f"You are a representative of {company_name}. " if company_name else ""
        
        prompt_parts = [company_context]
        if system_prompt:
            prompt_parts.append(system_prompt)
        
        if is_follow_up:
            prompt_parts.append("The user has been inactive for 3 minutes. Send a very brief, friendly follow-up message to see if they need more help. Just one short sentence.")
        
        prompt_parts.append(f"Context:\\n{context}")
        if history:
            prompt_parts.append(f"Chat History:\\n{history}")
        
        full_prompt = "\\n\\n".join(prompt_parts)
        
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