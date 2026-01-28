from typing import List, Dict
from langchain.schema import BaseRetriever, Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from src.domain.abstractions.services.rag_service import IRAGService
from src.infrastructure.services.WebsiteLoader import WebsiteLoaderService
from src.infrastructure.services.DocumentChunker import DocumentChunkingService
from src.infrastructure.services.EmbeddingService import EmbeddingService
from src.infrastructure.services.VectorStore import VectorStoreService
from src.infrastructure.clients.llm_client import LLMClient


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