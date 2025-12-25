from services.load_website_content_service import LoadWebsiteContentService
from services.document_chunking_service import DocumentChunkingService
from services.embedding_service import EmbeddingService
from services.response_generation_service import ResponseGenerationService
from services.vector_store_service import VectorStore
from helpers.ai_client_helper import get_openai_client
from configs.constants import PERSIST_DIR

class RAGPipeline:
    def __init__(self):
        self.loader = None
        self.chunker = DocumentChunkingService()
        self.embeddings = EmbeddingService()
        self.async_client = None
        self.vectorstore = None
        self.company_name = None

    async def build(self, url: str, company_name: str):
        """Build and persist the vector store for a company URL."""
        self.loader = LoadWebsiteContentService(url)
        self.async_client = await get_openai_client()
        self.company_name = company_name
        documents = await self.loader.scrape_website(url)
        chunks = self.chunker.create_chunks(documents)
        vector_store = VectorStore(self.embeddings.get_embeddings(), persist_dir=PERSIST_DIR)
        self.vectorstore = vector_store.create_store(documents=chunks, collection_name=company_name)

    async def query(self, question: str, company_name: str) -> str:
        """Query a previously built collection."""
        if self.vectorstore is None:
            store = VectorStore(self.embeddings.get_embeddings(), persist_dir=PERSIST_DIR)
            self.vectorstore = store.load_store(collection_name=company_name)

        retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3}
        )
        generator = ResponseGenerationService(self.async_client)
        qa_chain = generator.create_chain(retriever)
        result = await qa_chain.arun(question)
        return result
