"""
Main Firecrawl Q&A Module
========================

Main orchestrator class that combines crawling and Q&A generation.
Provides high-level interface for the complete workflow.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from .crawler import FirecrawlCrawler, CrawlResult, ALL_TARGET_URLS, CONSULTANCY_URLS, GOVERNMENT_URLS
    from .qa_generator import QAGenerator, QAPair
    from .data_processor import DataProcessor
except ImportError:
    from crawler import FirecrawlCrawler, CrawlResult, ALL_TARGET_URLS, CONSULTANCY_URLS, GOVERNMENT_URLS
    from qa_generator import QAGenerator, QAPair
    from data_processor import DataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('firecrawl_qa_module.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FirecrawlQAModule:
    """
    Main class that orchestrates the complete Firecrawl Q&A generation workflow
    """
    
    def __init__(self, 
                 firecrawl_api_key: Optional[str] = None,
                 gemini_api_key: Optional[str] = None,
                 output_dir: str = "firecrawl_output"):
        """
        Initialize the Firecrawl Q&A Module
        
        Args:
            firecrawl_api_key: Firecrawl API key (loads from .env if not provided)
            gemini_api_key: Gemini API key (loads from .env if not provided)
            output_dir: Directory to save output files
        """
        logger.info("Initializing Firecrawl Q&A Module...")
        
        # Initialize components
        try:
            self.crawler = FirecrawlCrawler(api_key=firecrawl_api_key)
            self.qa_generator = QAGenerator(api_key=gemini_api_key)
            self.data_processor = DataProcessor(output_dir=output_dir)
            logger.info("All components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def crawl_and_generate_qa(self, 
                            urls: List[str],
                            min_confidence: float = 0.3,
                            save_intermediate: bool = True) -> Dict[str, Any]:
        """
        Complete workflow: crawl URLs and generate Q&A pairs
        
        Args:
            urls: List of URLs to crawl
            min_confidence: Minimum confidence score for Q&A filtering
            save_intermediate: Whether to save intermediate results
            
        Returns:
            Dictionary with results and file paths
        """
        logger.info(f"Starting complete workflow for {len(urls)} URLs")
        start_time = datetime.now()
        
        results = {
            'crawl_results': [],
            'qa_pairs': [],
            'files_created': [],
            'summary': {}
        }
        
        try:
            # Step 1: Crawl URLs
            logger.info("Step 1: Crawling URLs...")
            crawl_results = self.crawler.crawl_multiple_urls(urls)
            results['crawl_results'] = crawl_results
            
            # Log crawl summary
            crawl_summary = self.crawler.get_content_summary(crawl_results)
            logger.info(f"Crawl completed: {crawl_summary['success_rate']} success rate")
            
            if save_intermediate:
                self._save_crawl_results(crawl_results)
            
            # Step 2: Generate Q&A pairs
            logger.info("Step 2: Generating Q&A pairs...")
            all_qa_pairs = []
            
            for i, crawl_result in enumerate(crawl_results, 1):
                if crawl_result.success and crawl_result.content.strip():
                    logger.info(f"Processing content from {crawl_result.url} ({i}/{len(crawl_results)})")
                    
                    source_info = {
                        'title': crawl_result.title,
                        'url': crawl_result.url,
                        'metadata': crawl_result.metadata
                    }
                    
                    qa_pairs = self.qa_generator.generate_qa_pairs(
                        crawl_result.content,
                        source_info
                    )
                    
                    all_qa_pairs.extend(qa_pairs)
                    logger.info(f"Generated {len(qa_pairs)} Q&A pairs from {crawl_result.url}")
                else:
                    logger.warning(f"Skipping {crawl_result.url} - crawl failed or empty content")
            
            # Step 3: Filter Q&A pairs
            logger.info("Step 3: Filtering Q&A pairs...")
            filtered_qa_pairs = self.qa_generator.filter_qa_pairs(all_qa_pairs, min_confidence)
            results['qa_pairs'] = filtered_qa_pairs
            
            # Step 4: Save results
            logger.info("Step 4: Saving results...")
            
            # Save Q&A data
            qa_file = self.data_processor.save_qa_data(filtered_qa_pairs)
            results['files_created'].append(qa_file)
            
            # Export to CSV
            csv_file = self.data_processor.export_to_csv(filtered_qa_pairs)
            results['files_created'].append(csv_file)
            
            # Generate and save summary report
            summary_report = self.data_processor.generate_summary_report(filtered_qa_pairs, crawl_results)
            summary_report['processing_time'] = str(datetime.now() - start_time)
            
            report_file = self.data_processor.save_summary_report(summary_report)
            results['files_created'].append(report_file)
            results['summary'] = summary_report
            
            # Log final summary
            total_time = datetime.now() - start_time
            logger.info(f"Workflow completed successfully in {total_time}")
            logger.info(f"Generated {len(filtered_qa_pairs)} high-quality Q&A pairs")
            logger.info(f"Files created: {results['files_created']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            raise
    
    def crawl_predefined_urls(self, 
                            url_set: str = "all",
                            min_confidence: float = 0.3) -> Dict[str, Any]:
        """
        Crawl predefined URL sets and generate Q&A pairs
        
        Args:
            url_set: Which URL set to use ("all", "consultancy", "government")
            min_confidence: Minimum confidence score for filtering
            
        Returns:
            Results dictionary
        """
        url_sets = {
            "all": ALL_TARGET_URLS,
            "consultancy": CONSULTANCY_URLS,
            "government": GOVERNMENT_URLS
        }
        
        if url_set not in url_sets:
            raise ValueError(f"Invalid url_set. Choose from: {list(url_sets.keys())}")
        
        urls = url_sets[url_set]
        logger.info(f"Using predefined URL set '{url_set}' with {len(urls)} URLs")
        
        return self.crawl_and_generate_qa(urls, min_confidence)
    
    def update_existing_qa_data(self, 
                               urls: List[str],
                               existing_file: str,
                               min_confidence: float = 0.3) -> str:
        """
        Crawl new URLs and merge with existing Q&A data
        
        Args:
            urls: List of URLs to crawl
            existing_file: Path to existing Q&A JSON file
            min_confidence: Minimum confidence score for filtering
            
        Returns:
            Path to updated file
        """
        logger.info(f"Updating existing Q&A data from {existing_file}")
        
        # Crawl URLs
        crawl_results = self.crawler.crawl_multiple_urls(urls)
        
        # Generate Q&A pairs
        all_qa_pairs = []
        for crawl_result in crawl_results:
            if crawl_result.success and crawl_result.content.strip():
                source_info = {
                    'title': crawl_result.title,
                    'url': crawl_result.url,
                    'metadata': crawl_result.metadata
                }
                
                qa_pairs = self.qa_generator.generate_qa_pairs(
                    crawl_result.content,
                    source_info
                )
                all_qa_pairs.extend(qa_pairs)
        
        # Filter Q&A pairs
        filtered_qa_pairs = self.qa_generator.filter_qa_pairs(all_qa_pairs, min_confidence)
        
        # Merge with existing data
        updated_file = self.data_processor.merge_with_existing_data(filtered_qa_pairs, existing_file)
        
        logger.info(f"Added {len(filtered_qa_pairs)} new Q&A pairs to {updated_file}")
        return updated_file
    
    def crawl_single_url(self, url: str, min_confidence: float = 0.3) -> Dict[str, Any]:
        """
        Crawl a single URL and generate Q&A pairs
        
        Args:
            url: URL to crawl
            min_confidence: Minimum confidence score for filtering
            
        Returns:
            Results dictionary
        """
        logger.info(f"Processing single URL: {url}")
        
        # Crawl URL
        crawl_result = self.crawler.crawl_url(url)
        
        if not crawl_result.success:
            logger.error(f"Failed to crawl {url}: {crawl_result.error_message}")
            return {
                'success': False,
                'error': crawl_result.error_message,
                'qa_pairs': [],
                'files_created': []
            }
        
        # Generate Q&A pairs
        source_info = {
            'title': crawl_result.title,
            'url': crawl_result.url,
            'metadata': crawl_result.metadata
        }
        
        qa_pairs = self.qa_generator.generate_qa_pairs(crawl_result.content, source_info)
        filtered_qa_pairs = self.qa_generator.filter_qa_pairs(qa_pairs, min_confidence)
        
        # Save results
        qa_file = self.data_processor.save_qa_data(filtered_qa_pairs, f"single_url_{url.replace('https://', '').replace('/', '_')}.json")
        
        return {
            'success': True,
            'qa_pairs': filtered_qa_pairs,
            'files_created': [qa_file],
            'crawl_result': crawl_result
        }
    
    def _save_crawl_results(self, crawl_results: List[CrawlResult]) -> str:
        """
        Save raw crawl results to file
        
        Args:
            crawl_results: List of crawl results
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crawl_results_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert crawl results to serializable format
        results_data = []
        for result in crawl_results:
            results_data.append({
                'url': result.url,
                'title': result.title,
                'content_length': len(result.content),
                'success': result.success,
                'error_message': result.error_message,
                'metadata': result.metadata
            })
        
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Saved crawl results to {filepath}")
        return filepath
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get module statistics and configuration
        
        Returns:
            Statistics dictionary
        """
        return {
            'module_version': '1.0.0',
            'output_directory': self.output_dir,
            'crawler_rate_limit': self.crawler.rate_limit_delay,
            'qa_generator_chunk_size': self.qa_generator.chunk_size,
            'qa_generator_max_pairs_per_chunk': self.qa_generator.max_qa_pairs_per_chunk,
            'supported_categories': list(self.qa_generator.categories.keys()),
            'predefined_url_sets': {
                'consultancy_urls': len(CONSULTANCY_URLS),
                'government_urls': len(GOVERNMENT_URLS),
                'total_urls': len(ALL_TARGET_URLS)
            }
        }
