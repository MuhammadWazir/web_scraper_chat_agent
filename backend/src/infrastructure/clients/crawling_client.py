"""Crawl4AI crawling client implementation"""
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from src.domain.abstractions.clients.abstract_crawling_client import AbstractCrawlingClient
from src.infrastructure.utils.text_cleaner import clean_text_for_rag
from langchain.schema import Document

class CrawlingClient(AbstractCrawlingClient):
    """Crawl4AI implementation of crawling client"""
    
    def __init__(
        self,
        max_depth: int = 2,
        max_pages: int = 20,
        include_external: bool = False
    ):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.include_external = include_external
        
        self.crawler_config = CrawlerRunConfig(
            deep_crawl_strategy=BestFirstCrawlingStrategy(
                max_depth=max_depth,
                include_external=include_external,
                max_pages=max_pages
            ),
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=True
        )

    async def scrape_website(self, url: str) -> List[Document]:
        """Scrape website and return documents with cleaned content"""
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                config=self.crawler_config,
                bypass_cache=True
            )
            if not result:
                return []
            
            documents = []
            for page_result in result:
                if hasattr(page_result, 'markdown') and page_result.markdown:
                    cleaned_content = clean_text_for_rag(page_result.markdown)
                    documents.append(Document(
                        page_content=cleaned_content,
                        metadata={
                            "source": url,
                            "page_url": getattr(page_result, 'url', url)
                        }
                    ))
            return documents
