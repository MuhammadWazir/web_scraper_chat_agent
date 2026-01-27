"""RAG service implementation using LangChain and Qdrant - DEBUG VERSION"""
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
    """Custom retriever for Qdrant vector store"""
    
    vector_store: VectorStoreService
    collection_name: str
    k: int = 3
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """Get documents relevant to a query"""
        results = self.vector_store.search(query, self.collection_name, k=self.k)
        return [Document(page_content=result.text, metadata=result.metadata) for result in results]
    
    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        """Async get documents relevant to a query"""
        return self._get_relevant_documents(query, run_manager=run_manager)


class RAGService(IRAGService):
    """Concrete implementation of RAG service"""
    
    def __init__(self):
        self.loader = None
        self.chunker = DocumentChunkingService()
        self.embeddings = EmbeddingService()
        self.llm_client = LLMClient()
        self.vector_store_service = None
        self.company_name = None

    async def build(self, url: str, company_name: str) -> None:
        """Build and persist the vector store for a company URL"""
        self.loader = WebsiteLoaderService(url)
        self.company_name = company_name
        documents = await self.loader.scrape_website(url)
        chunks = self.chunker.create_chunks(documents)
        
        # Create vector store service and upload documents
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
        """Query the RAG system with a question and optional chat history"""
        print(f"\n[DEBUG RAGService] ========== QUERY START ==========")
        print(f"[DEBUG RAGService] Question: {question}")
        print(f"[DEBUG RAGService] Company: {company_name}")
        print(f"[DEBUG RAGService] Has tools: {bool(tools)}")
        print(f"[DEBUG RAGService] Chat history length: {len(chat_history) if chat_history else 0}")
        
        if self.vector_store_service is None:
            self.vector_store_service = VectorStoreService(self.embeddings.get_embeddings())
        
        # Create custom retriever for Qdrant
        retriever = QdrantRetriever(
            vector_store=self.vector_store_service,
            collection_name=company_name,
            k=3
        )
            
        print(f"[DEBUG RAGService] Creating chain...")
        qa_chain = self.llm_client.create_chain(
            retriever,
            chat_history=chat_history,
            company_name=company_name,
            tools=tools
        )
        print(f"[DEBUG RAGService] Chain created, type: {type(qa_chain)}")
        
        # Invoke chain
        try:
            if tools:
                print(f"[DEBUG RAGService] Invoking chain WITH tools...")
                result = await qa_chain.ainvoke(
                    {"input": question, "chat_history": chat_history or []},
                    config={"configurable": {"auth_token": auth_token}}
                )
            else:
                print(f"[DEBUG RAGService] Invoking chain WITHOUT tools...")
                result = await qa_chain.ainvoke(question)
            
            print(f"[DEBUG RAGService] Chain invoked successfully")
            print(f"[DEBUG RAGService] Result type: {type(result)}")
            print(f"[DEBUG RAGService] Result value: {result}")
            
            # Process result
            if isinstance(result, dict):
                print(f"[DEBUG RAGService] Result is dict, keys: {result.keys()}")
                answer = result.get("result", result.get("output", str(result)))
                print(f"[DEBUG RAGService] Extracted answer type: {type(answer)}")
                print(f"[DEBUG RAGService] Extracted answer: {str(answer)[:100]}...")
                final_answer = str(answer) if answer else "I don't know."
            elif isinstance(result, str):
                print(f"[DEBUG RAGService] Result is string")
                final_answer = result
            else:
                print(f"[DEBUG RAGService] Result is unknown type, converting to string")
                final_answer = str(result)
            
            print(f"[DEBUG RAGService] Final answer type: {type(final_answer)}")
            print(f"[DEBUG RAGService] Final answer: {final_answer[:100]}...")
            print(f"[DEBUG RAGService] ========== QUERY END ==========\n")
            
            return final_answer
            
        except Exception as e:
            print(f"[ERROR RAGService] Exception during query: {e}")
            import traceback
            traceback.print_exc()
            print(f"[DEBUG RAGService] ========== QUERY END (ERROR) ==========\n")
            raise