#!/usr/bin/env python3
"""
URL Management Script
==================

Easy interface to add new URLs and run crawling operations.
This shows you how to easily add new URLs for future crawling.
"""

import os
import sys
from typing import List
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import FirecrawlQAModule
    from crawler import CONSULTANCY_URLS, GOVERNMENT_URLS
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the firecrawl_qa_module directory")
    sys.exit(1)

class URLManager:
    """Simple URL management and crawling interface"""
    
    def __init__(self):
        self.module = FirecrawlQAModule(output_dir="custom_crawl_output")
        
    def crawl_single_url(self, url: str) -> dict:
        """
        Crawl a single URL and generate Q&A pairs
        
        Args:
            url: URL to crawl
            
        Returns:
            Dictionary with results
        """
        print(f"🌐 Crawling single URL: {url}")
        print(f"📅 Started at: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            result = self.module.crawl_single_url(url)
            print(f"✅ Successfully crawled: {url}")
            return result
        except Exception as e:
            print(f"❌ Error crawling {url}: {str(e)}")
            return {"error": str(e)}
    
    def crawl_multiple_urls(self, urls: List[str]) -> dict:
        """
        Crawl multiple URLs and generate Q&A pairs
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            Dictionary with results
        """
        print(f"🌐 Crawling {len(urls)} URLs:")
        for i, url in enumerate(urls, 1):
            print(f"   {i}. {url}")
        
        print(f"📅 Started at: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            results = self.module.crawl_and_generate_qa(
                urls=urls,
                min_confidence=0.4
            )
            print(f"✅ Successfully crawled {len(urls)} URLs")
            return results
        except Exception as e:
            print(f"❌ Error crawling URLs: {str(e)}")
            return {"error": str(e)}
    
    def show_predefined_urls(self):
        """Display all predefined URLs"""
        print("📋 Predefined URL Lists:")
        print("\n🏢 Consultancy URLs:")
        for i, url in enumerate(CONSULTANCY_URLS, 1):
            print(f"   {i}. {url}")
        
        print("\n🏛️  Government URLs:")
        for i, url in enumerate(GOVERNMENT_URLS, 1):
            print(f"   {i}. {url}")

def main():
    """Interactive main function"""
    manager = URLManager()
    
    print("🔧 Firecrawl Q&A Module - URL Manager")
    print("=" * 50)
    
    while True:
        print("\n📋 Choose an option:")
        print("1. 🌐 Crawl a single URL")
        print("2. 🌍 Crawl multiple URLs")
        print("3. 📋 Show predefined URLs")
        print("4. 🚀 Crawl ALL predefined URLs")
        print("5. ❌ Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            url = input("Enter URL to crawl: ").strip()
            if url:
                manager.crawl_single_url(url)
            else:
                print("❌ Please enter a valid URL")
                
        elif choice == "2":
            print("Enter URLs (one per line, press Enter twice when done):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if urls:
                manager.crawl_multiple_urls(urls)
            else:
                print("❌ No URLs entered")
                
        elif choice == "3":
            manager.show_predefined_urls()
            
        elif choice == "4":
            all_urls = CONSULTANCY_URLS + GOVERNMENT_URLS
            print(f"🚀 This will crawl all {len(all_urls)} predefined URLs")
            confirm = input("Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                manager.crawl_multiple_urls(all_urls)
            else:
                print("❌ Cancelled")
                
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-5")

# Example of how to add new URLs programmatically
def add_custom_urls_example():
    """
    Example function showing how to add custom URLs for crawling
    """
    # Your custom URLs
    custom_urls = [
        "https://your-new-consultancy.com",
        "https://another-education-site.edu",
        "https://scholarship-portal.org"
    ]
    
    # Initialize manager
    manager = URLManager()
    
    # Crawl your custom URLs
    results = manager.crawl_multiple_urls(custom_urls)
    
    return results

if __name__ == "__main__":
    # Uncomment the line below to run the interactive version
    main()
    
    # Uncomment the line below to run the custom URLs example
    # add_custom_urls_example()
