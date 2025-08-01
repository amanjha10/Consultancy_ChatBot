"""
Firecrawl Crawler Module
========================

Handles web scraping using Firecrawl API with support for:
- Single URL crawling
- Batch URL processing  
- Rate limiting and retry mechanisms
- Content extraction and cleaning
"""

import os
import time
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CrawlResult:
    """Data class for crawl results"""
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class FirecrawlCrawler:
    """
    Firecrawl API wrapper for web scraping
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Firecrawl crawler
        
        Args:
            api_key: Firecrawl API key (if not provided, loads from .env)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        if not self.api_key:
            raise ValueError("Firecrawl API key not found. Please set FIRECRAWL_API_KEY in .env file")
        
        self.base_url = "https://api.firecrawl.dev/v0"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.rate_limit_delay = 2  # seconds between requests
        
    def crawl_url(self, url: str, options: Optional[Dict] = None) -> CrawlResult:
        """
        Crawl a single URL using Firecrawl API
        
        Args:
            url: URL to crawl
            options: Additional crawling options
            
        Returns:
            CrawlResult object with crawled data
        """
        try:
            logger.info(f"Crawling URL: {url}")
            
            # Default options for educational content
            default_options = {
                "pageOptions": {
                    "onlyMainContent": True,
                    "includeHtml": False,
                    "includeRawHtml": False
                }
            }
            
            if options:
                default_options.update(options)
            
            # Make API request
            payload = {
                "url": url,
                **default_options
            }
            
            response = requests.post(
                f"{self.base_url}/scrape",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    content_data = data.get('data', {})
                    
                    return CrawlResult(
                        url=url,
                        title=content_data.get('metadata', {}).get('title', 'Unknown Title'),
                        content=content_data.get('content', ''),
                        metadata=content_data.get('metadata', {}),
                        success=True
                    )
                else:
                    error_msg = data.get('error', 'Unknown error occurred')
                    logger.error(f"Firecrawl error for {url}: {error_msg}")
                    return CrawlResult(
                        url=url,
                        title='',
                        content='',
                        metadata={},
                        success=False,
                        error_message=error_msg
                    )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Request failed for {url}: {error_msg}")
                return CrawlResult(
                    url=url,
                    title='',
                    content='',
                    metadata={},
                    success=False,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"Exception while crawling {url}: {str(e)}")
            return CrawlResult(
                url=url,
                title='',
                content='',
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    def crawl_multiple_urls(self, urls: List[str], delay: Optional[float] = None) -> List[CrawlResult]:
        """
        Crawl multiple URLs with rate limiting
        
        Args:
            urls: List of URLs to crawl
            delay: Delay between requests (uses default if not provided)
            
        Returns:
            List of CrawlResult objects
        """
        delay = delay or self.rate_limit_delay
        results = []
        
        logger.info(f"Starting batch crawl of {len(urls)} URLs")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}: {url}")
            
            result = self.crawl_url(url)
            results.append(result)
            
            # Rate limiting
            if i < len(urls):  # Don't delay after the last request
                logger.info(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
        
        successful_crawls = sum(1 for r in results if r.success)
        logger.info(f"Batch crawl completed: {successful_crawls}/{len(urls)} successful")
        
        return results
    
    def crawl_with_retry(self, url: str, max_retries: int = 3, retry_delay: float = 5.0) -> CrawlResult:
        """
        Crawl URL with retry mechanism
        
        Args:
            url: URL to crawl
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries
            
        Returns:
            CrawlResult object
        """
        for attempt in range(max_retries + 1):
            result = self.crawl_url(url)
            
            if result.success:
                return result
            
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1} failed for {url}, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries + 1} attempts failed for {url}")
        
        return result
    
    def get_content_summary(self, results: List[CrawlResult]) -> Dict[str, Any]:
        """
        Generate summary statistics for crawl results
        
        Args:
            results: List of CrawlResult objects
            
        Returns:
            Summary statistics dictionary
        """
        total_urls = len(results)
        successful_crawls = sum(1 for r in results if r.success)
        failed_crawls = total_urls - successful_crawls
        
        total_content_length = sum(len(r.content) for r in results if r.success)
        avg_content_length = total_content_length / successful_crawls if successful_crawls > 0 else 0
        
        return {
            'total_urls': total_urls,
            'successful_crawls': successful_crawls,
            'failed_crawls': failed_crawls,
            'success_rate': f"{(successful_crawls/total_urls)*100:.1f}%" if total_urls > 0 else "0%",
            'total_content_length': total_content_length,
            'avg_content_length': int(avg_content_length),
            'failed_urls': [r.url for r in results if not r.success]
        }

# Predefined URL lists for different categories
CONSULTANCY_URLS = [
    "https://kiec.edu.np",
    "https://edwisefoundation.com", 
    "https://experteducation.com/nepal/",
    "https://www.aeccglobal.com.np",
    "https://niec.edu.np"
]

GOVERNMENT_URLS = [
    "https://educationusa.state.gov",
    "https://www.studyinaustralia.gov.au", 
    "https://www.ukcisa.org.uk",
    "https://www.daad.de/en",
    "https://www.educanada.ca"
]

ALL_TARGET_URLS = CONSULTANCY_URLS + GOVERNMENT_URLS
