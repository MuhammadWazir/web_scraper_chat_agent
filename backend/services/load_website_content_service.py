from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from helpers.chunk_summarizer_helper import summarize_chunks_in_parallel
from langchain.schema import Document
from typing import List
class LoadWebsiteContentService:
    def __init__(self, website_url: str):
        self.website_url = website_url
        self.crawler_config = CrawlerRunConfig(
            deep_crawl_strategy=BestFirstCrawlingStrategy(
                max_depth=2,
                include_external=False,
                max_pages=20
            ),
            scraping_strategy=LXMLWebScrapingStrategy(),
            verbose=True
        )
    async def scrape_website(self, url: str) -> List[Document]:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                config=self.crawler_config,
                bypass_cache=True
            )
            if not result:
                return ""
            chunks = []
            for page_result in result:
                if hasattr(page_result, 'markdown') and page_result.markdown:
                    chunks.append(page_result.markdown)
            summarized_chunks = await summarize_chunks_in_parallel(chunks)
            if not summarized_chunks:
                return []
            return [Document(page_content=summarized_chunks, metadata={"source": self.website_url})]