"""
Firecrawl Q&A Module
===================

A comprehensive module for crawling consultancy websites and generating 
structured Q&A pairs using Firecrawl API and Gemini AI.

Features:
- Web scraping with Firecrawl API
- AI-powered Q&A generation with Gemini
- Structured JSON output with categorization
- Support for multiple website types
- Error handling and retry mechanisms
"""

__version__ = "1.0.0"
__author__ = "EduConsult Team"

try:
    from .crawler import FirecrawlCrawler
    from .qa_generator import QAGenerator
    from .data_processor import DataProcessor
    from .main import FirecrawlQAModule
except ImportError:
    from crawler import FirecrawlCrawler
    from qa_generator import QAGenerator
    from data_processor import DataProcessor
    from main import FirecrawlQAModule

__all__ = [
    'FirecrawlCrawler',
    'QAGenerator', 
    'DataProcessor',
    'FirecrawlQAModule'
]
