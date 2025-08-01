#!/usr/bin/env python3
"""
Quick URL Crawler
===============

Simple interface to crawl new URLs. Use this to easily add and crawl new websites.
This demonstrates how to add new URLs for future crawling operations.
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import FirecrawlQAModule
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def crawl_new_url(url: str, output_prefix: str = "custom"):
    """
    Crawl a single new URL and generate Q&A pairs
    
    Args:
        url: URL to crawl
        output_prefix: Prefix for output files
    """
    print(f"🌐 Crawling: {url}")
    print(f"📅 Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Initialize module with custom output directory
    module = FirecrawlQAModule(output_dir=f"{output_prefix}_output")
    
    try:
        # Crawl single URL
        result = module.crawl_single_url(url)
        
        if result.get('success', False):
            print(f"✅ Successfully crawled and processed: {url}")
            print(f"📊 Generated Q&A pairs: {len(result.get('qa_pairs', []))}")
            print(f"📁 Output saved to: {output_prefix}_output/")
            
            # Show some sample Q&A pairs
            qa_pairs = result.get('qa_pairs', [])
            if qa_pairs:
                print(f"\n🔍 Sample Q&A pairs:")
                for i, qa in enumerate(qa_pairs[:3], 1):
                    print(f"  {i}. Q: {qa.get('question', 'N/A')[:100]}...")
                    print(f"     A: {qa.get('answer', 'N/A')[:100]}...")
                    print()
        else:
            print(f"❌ Failed to crawl: {url}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def crawl_multiple_new_urls(urls: list, output_prefix: str = "batch"):
    """
    Crawl multiple new URLs
    
    Args:
        urls: List of URLs to crawl
        output_prefix: Prefix for output files
    """
    print(f"🌐 Crawling {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")
    
    print(f"📅 Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Initialize module
    module = FirecrawlQAModule(output_dir=f"{output_prefix}_output")
    
    try:
        # Crawl multiple URLs
        results = module.crawl_and_generate_qa(urls=urls, min_confidence=0.4)
        
        print(f"✅ Crawling completed!")
        
        # Show summary
        if 'summary' in results:
            summary = results['summary']
            qa_stats = summary.get('qa_generation_statistics', {})
            crawl_stats = summary.get('crawl_statistics', {})
            
            print(f"📊 Summary:")
            print(f"   Total Q&A pairs: {qa_stats.get('total_qa_pairs', 'N/A')}")
            print(f"   Success rate: {crawl_stats.get('success_rate', 'N/A')}")
            print(f"   Processing time: {summary.get('processing_time', 'N/A')}")
            print(f"📁 Output saved to: {output_prefix}_output/")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Example usage functions
def example_single_url():
    """Example: Crawl a single new URL"""
    new_url = "https://www.britishcouncil.org.np"  # Example new URL
    crawl_new_url(new_url, "british_council")

def example_multiple_urls():
    """Example: Crawl multiple new URLs"""
    new_urls = [
        "https://www.iom.edu.np",           # Institute of Medicine
        "https://www.tribhuvan-university.edu.np",  # TU
        "https://www.kusoed.edu.np"         # Kathmandu University School of Education
    ]
    crawl_multiple_new_urls(new_urls, "nepal_universities")

if __name__ == "__main__":
    print("🔧 Quick URL Crawler")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        # Command line usage: python quick_crawler.py "https://example.com"
        url = sys.argv[1]
        crawl_new_url(url, "cli_crawl")
    else:
        # Interactive mode
        print("\n📋 Choose an option:")
        print("1. 🌐 Crawl a single URL")
        print("2. 🌍 Crawl multiple URLs")
        print("3. 📖 Run example: Single URL")
        print("4. 📚 Run example: Multiple URLs")
        print("5. ❌ Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            url = input("Enter URL to crawl: ").strip()
            if url:
                output_name = input("Enter output name (default: custom): ").strip() or "custom"
                crawl_new_url(url, output_name)
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
                output_name = input("Enter output name (default: batch): ").strip() or "batch"
                crawl_multiple_new_urls(urls, output_name)
            else:
                print("❌ No URLs entered")
                
        elif choice == "3":
            example_single_url()
            
        elif choice == "4":
            example_multiple_urls()
            
        elif choice == "5":
            print("👋 Goodbye!")
            
        else:
            print("❌ Invalid choice. Please enter 1-5")
