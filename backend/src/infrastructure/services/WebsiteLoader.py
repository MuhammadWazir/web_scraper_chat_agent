"""Website content loading service"""
from typing import List
from langchain.schema import Document
from src.infrastructure.clients.crawling_client import CrawlingClient
from src.infrastructure.clients.llm_client import LLMClient


class WebsiteLoaderService:
    """Service for scraping and loading website content"""
    
    def __init__(self, website_url: str):
        self.website_url = website_url
        self.crawling_client = CrawlingClient(max_depth=2, max_pages=20, include_external=False)
        self.llm_client = LLMClient()
    
    async def scrape_website(self, url: str) -> List[Document]:
        """Scrape website and return documents with summarized content"""
        # Use crawling client to scrape the website
        scraped_documents = await self.crawling_client.scrape_website(url)
        
        if not scraped_documents:
            return []
        
        # Extract content from scraped documents
        chunks = [doc.page_content for doc in scraped_documents if doc.page_content]
        
        if not chunks:
            return []
        
        # Summarize the chunks using LLM client
        summarized_content = await self.llm_client.summarize_chunks_in_parallel(chunks, "gpt-4o")
        
        if not summarized_content:
            return []
        
        # Return as LangChain Document
        return [Document(page_content=summarized_content, metadata={"source": self.website_url})]




