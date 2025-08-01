#!/usr/bin/env python3
"""
Crawl All URLs Script
===================

Script to crawl all predefined URLs and generate comprehensive Q&A dataset.
This will process all consultancy and government education websites.
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import FirecrawlQAModule
    from crawler import CONSULTANCY_URLS, GOVERNMENT_URLS, ALL_TARGET_URLS
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the firecrawl_qa_module directory")
    sys.exit(1)

def main():
    """Main function to crawl all URLs"""
    print("🚀 Starting comprehensive crawl of all educational websites...")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # URLs to process
    print(f"\n📋 URLs to process:")
    print(f"   Consultancy URLs: {len(CONSULTANCY_URLS)}")
    for url in CONSULTANCY_URLS:
        print(f"     ✓ {url}")
    
    print(f"   Government URLs: {len(GOVERNMENT_URLS)}")
    for url in GOVERNMENT_URLS:
        print(f"     ✓ {url}")
    
    print(f"\n📊 Total URLs: {len(ALL_TARGET_URLS)}")
    
    # Initialize module
    print("\n🔧 Initializing Firecrawl Q&A Module...")
    module = FirecrawlQAModule(output_dir="complete_crawl_output")
    
    # Process all URLs
    print("\n🌐 Starting crawl and Q&A generation...")
    print("⏱️  This may take 15-30 minutes depending on website sizes...")
    
    try:
        results = module.crawl_and_generate_qa(
            urls=ALL_TARGET_URLS,
            min_confidence=0.4
        )
        
        print("\n✅ Crawling completed successfully!")
        print(f"📁 Output saved to: complete_crawl_output/")
        
        # Print summary
        if 'summary' in results:
            summary = results['summary']
            print(f"\n📈 Summary Statistics:")
            print(f"   Total Q&A pairs: {summary.get('qa_generation_statistics', {}).get('total_qa_pairs', 'N/A')}")
            print(f"   Success rate: {summary.get('crawl_statistics', {}).get('success_rate', 'N/A')}")
            print(f"   Processing time: {summary.get('processing_time', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error during crawling: {str(e)}")
        print("🔍 Check the logs for detailed error information")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
