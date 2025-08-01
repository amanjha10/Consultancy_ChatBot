#!/usr/bin/env python3
"""
Quick Test Script for Firecrawl Q&A Module
==========================================

A simple script to test the Firecrawl Q&A module with a single URL.
This is useful for validating the setup and API connections.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_firecrawl_module():
    """
    Test the Firecrawl Q&A module with a single reliable URL
    """
    print("🧪 Testing Firecrawl Q&A Module")
    print("=" * 40)
    
    try:
        # Import the module
        print("📦 Importing Firecrawl Q&A Module...")
        from main import FirecrawlQAModule
        
        # Initialize the module
        print("⚙️ Initializing module...")
        module = FirecrawlQAModule(output_dir="test_output")
        
        # Test URL (choose a reliable educational site)
        test_url = "https://www.daad.de/en"
        print(f"🌐 Testing with URL: {test_url}")
        
        # Process single URL
        print("🔄 Crawling and generating Q&A pairs...")
        result = module.crawl_single_url(
            url=test_url,
            min_confidence=0.3
        )
        
        # Check results
        if result['success']:
            qa_pairs = result['qa_pairs']
            print(f"✅ Success! Generated {len(qa_pairs)} Q&A pairs")
            
            if qa_pairs:
                # Show first Q&A pair as example
                sample_qa = qa_pairs[0]
                print(f"\n📝 Sample Q&A Pair:")
                print(f"   Category: {sample_qa.category}")
                print(f"   Section: {sample_qa.section}")
                print(f"   Question: {sample_qa.question}")
                print(f"   Answer: {sample_qa.answer[:200]}{'...' if len(sample_qa.answer) > 200 else ''}")
                print(f"   Confidence: {sample_qa.confidence_score:.2f}")
                
                # Show category breakdown
                categories = {}
                for qa in qa_pairs:
                    categories[qa.category] = categories.get(qa.category, 0) + 1
                
                print(f"\n📊 Category Breakdown:")
                for category, count in categories.items():
                    print(f"   {category}: {count} pairs")
                
                # Show files created
                print(f"\n📁 Files Created:")
                for file_path in result['files_created']:
                    print(f"   {file_path}")
                
            else:
                print("⚠️ No Q&A pairs generated (may need to adjust confidence threshold)")
                
        else:
            print(f"❌ Failed: {result['error']}")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all required packages are installed:")
        print("   pip install requests python-dotenv google-generativeai")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print(f"\n🎉 Test completed successfully!")
    return True

def test_api_keys():
    """
    Test if API keys are properly configured
    """
    print("\n🔑 Testing API Key Configuration")
    print("-" * 35)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        firecrawl_key = os.getenv('FIRECRAWL_API_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        if firecrawl_key:
            print(f"✅ Firecrawl API Key: Found (length: {len(firecrawl_key)})")
        else:
            print("❌ Firecrawl API Key: Not found in .env file")
            return False
            
        if gemini_key:
            print(f"✅ Gemini API Key: Found (length: {len(gemini_key)})")
        else:
            print("❌ Gemini API Key: Not found in .env file")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking API keys: {e}")
        return False

def main():
    """
    Main test function
    """
    print("🚀 Firecrawl Q&A Module - Quick Test")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API keys first
    if not test_api_keys():
        print("\n💡 Please ensure your .env file contains:")
        print("   FIRECRAWL_API_KEY=your_firecrawl_key_here")
        print("   GEMINI_API_KEY=your_gemini_key_here")
        return 1
    
    # Test the module
    if test_firecrawl_module():
        print("\n🎊 All tests passed! The module is ready to use.")
        print("\n📚 Next steps:")
        print("   1. Run 'python example_usage.py' for more examples")
        print("   2. Check the 'test_output' directory for generated files")
        print("   3. Integrate with your existing chatbot system")
        return 0
    else:
        print("\n😞 Tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
