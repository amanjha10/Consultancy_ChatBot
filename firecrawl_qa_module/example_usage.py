#!/usr/bin/env python3
"""
Example Usage Script for Firecrawl Q&A Module
=============================================

This script demonstrates how to use the Firecrawl Q&A module
to crawl websites and generate structured Q&A pairs.
"""

import os
import sys
from datetime import datetime

# Add the module to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import FirecrawlQAModule
from crawler import CONSULTANCY_URLS, GOVERNMENT_URLS

def main():
    """
    Main function demonstrating different usage patterns
    """
    print("🚀 Firecrawl Q&A Module - Example Usage")
    print("=" * 50)
    
    try:
        # Initialize the module
        print("\n1. Initializing Firecrawl Q&A Module...")
        module = FirecrawlQAModule(output_dir="example_output")
        
        # Example 1: Crawl a single URL
        print("\n2. Example 1: Crawling a single URL...")
        single_url = "https://educationusa.state.gov"
        
        result = module.crawl_single_url(single_url, min_confidence=0.4)
        
        if result['success']:
            print(f"✅ Successfully processed {single_url}")
            print(f"   Generated {len(result['qa_pairs'])} Q&A pairs")
            print(f"   Saved to: {result['files_created']}")
        else:
            print(f"❌ Failed to process {single_url}: {result['error']}")
        
        # Example 2: Crawl consultancy websites
        print("\n3. Example 2: Crawling consultancy websites...")
        
        # Use a subset for the example (to save time and API calls)
        sample_consultancy_urls = CONSULTANCY_URLS[:2]  # First 2 URLs
        
        results = module.crawl_and_generate_qa(
            urls=sample_consultancy_urls,
            min_confidence=0.3,
            save_intermediate=True
        )
        
        print(f"✅ Processed {len(sample_consultancy_urls)} consultancy URLs")
        print(f"   Generated {len(results['qa_pairs'])} Q&A pairs")
        print(f"   Files created: {len(results['files_created'])}")
        
        # Print summary
        summary = results['summary']
        print(f"\n📊 Summary:")
        print(f"   Crawl success rate: {summary['crawl_statistics']['success_rate']}")
        print(f"   Total Q&A pairs: {summary['qa_generation_statistics']['total_qa_pairs']}")
        print(f"   Average confidence: {summary['qa_generation_statistics']['average_confidence_score']}")
        
        # Show category breakdown
        category_counts = summary['qa_generation_statistics']['qa_pairs_by_category']
        print(f"\n📂 Q&A pairs by category:")
        for category, count in category_counts.items():
            print(f"   {category}: {count}")
        
        # Example 3: Show some generated Q&A pairs
        print("\n4. Example 3: Sample generated Q&A pairs...")
        
        if results['qa_pairs']:
            print("\n🎯 Sample Q&A pairs:")
            for i, qa_pair in enumerate(results['qa_pairs'][:3], 1):  # Show first 3
                print(f"\n   Q{i}: {qa_pair.question}")
                print(f"   A{i}: {qa_pair.answer[:100]}{'...' if len(qa_pair.answer) > 100 else ''}")
                print(f"   Category: {qa_pair.category} | Section: {qa_pair.section}")
                print(f"   Confidence: {qa_pair.confidence_score:.2f}")
        
        print(f"\n✅ All examples completed successfully!")
        print(f"📁 Check the 'example_output' directory for generated files.")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        return 1
    
    return 0

def demo_predefined_urls():
    """
    Demonstrate using predefined URL sets
    """
    print("\n🌐 Demo: Using predefined URL sets")
    print("-" * 40)
    
    try:
        module = FirecrawlQAModule(output_dir="demo_output")
        
        # Get module statistics
        stats = module.get_statistics()
        print(f"📊 Module Statistics:")
        print(f"   Available URL sets: {stats['predefined_url_sets']}")
        print(f"   Supported categories: {len(stats['supported_categories'])}")
        
        # Process government URLs (smaller set for demo)
        print(f"\n🏛️ Processing government education portals...")
        
        results = module.crawl_predefined_urls(
            url_set="government",
            min_confidence=0.4
        )
        
        print(f"✅ Processed government URLs")
        print(f"   Generated files: {results['files_created']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return 1

def quick_test():
    """
    Quick test with a single reliable URL
    """
    print("\n⚡ Quick Test")
    print("-" * 20)
    
    try:
        module = FirecrawlQAModule(output_dir="test_output")
        
        # Test with a single, reliable URL
        test_url = "https://www.daad.de/en"
        
        print(f"🔍 Testing with: {test_url}")
        
        result = module.crawl_single_url(test_url, min_confidence=0.3)
        
        if result['success']:
            qa_count = len(result['qa_pairs'])
            print(f"✅ Test successful! Generated {qa_count} Q&A pairs")
            
            if qa_count > 0:
                sample_qa = result['qa_pairs'][0]
                print(f"\n📝 Sample Q&A:")
                print(f"   Q: {sample_qa.question}")
                print(f"   A: {sample_qa.answer[:150]}...")
                print(f"   Category: {sample_qa.category}")
        else:
            print(f"❌ Test failed: {result['error']}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return 1

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Full example (crawl multiple URLs)")
    print("2. Predefined URLs demo")
    print("3. Quick test (single URL)")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            exit_code = main()
        elif choice == "2":
            exit_code = demo_predefined_urls()
        elif choice == "3":
            exit_code = quick_test()
        else:
            print("Invalid choice. Running quick test...")
            exit_code = quick_test()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
