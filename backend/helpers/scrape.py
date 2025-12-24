import re
import httpx
import warnings
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from helpers.ai_processor import summarize_chunks_in_parallel

config = CrawlerRunConfig(
		deep_crawl_strategy = BestFirstCrawlingStrategy(
			max_depth=2,
			include_external=False,
			max_pages=20
		),
		scraping_strategy=LXMLWebScrapingStrategy(),
		verbose=True	
	)

async def scrape_website(url: str) -> str:
	async with AsyncWebCrawler() as crawler:
		result = await crawler.arun(
			url=url,
			config=config,
			bypass_cache=True
		)
		if not result:
			return ""
		chunks = []
		for page_result in result:
			if hasattr(page_result, 'markdown') and page_result.markdown:
				chunks.append(page_result.markdown)
		summarized_chunks = await summarize_chunks_in_parallel(chunks)
		return summarized_chunks

