#!/usr/bin/env python3
"""
Firecrawl Data Integration Script
Integrates scraped web data into the RAG system and reinitializes the vector database
"""

import json
import os
import uuid
from setup_rag import RAGSystem
import time

def check_firecrawl_integration():
    """Check if Firecrawl data is already integrated"""
    print("🔍 Checking current integration status...")
    
    faq_path = 'data/documents/education_faq.json'
    if not os.path.exists(faq_path):
        print("❌ education_faq.json not found!")
        return False, {}
    
    with open(faq_path, 'r') as f:
        current_data = json.load(f)
    
    # Check for firecrawl integrated sections
    firecrawl_sections = []
    for category, subcategories in current_data.items():
        if isinstance(subcategories, dict):
            for subcat, items in subcategories.items():
                if 'firecrawl' in subcat.lower() or any('firecrawl' in str(item).lower() for item in items if isinstance(item, dict)):
                    firecrawl_sections.append(f"{category}.{subcat}")
    
    if firecrawl_sections:
        print(f"✅ Found existing Firecrawl sections: {firecrawl_sections}")
        return True, current_data
    else:
        print("❌ No Firecrawl data found in current FAQ")
        return False, current_data

def load_firecrawl_data():
    """Load the latest Firecrawl data"""
    print("📥 Loading Firecrawl data...")
    
    # Try to find the most recent Firecrawl output
    firecrawl_files = [
        'firecrawl_qa_module/complete_crawl_output/firecrawl_qa_data_20250730_122917.json',
        'firecrawl_qa_module/example_output/firecrawl_qa_data_20250730_121244.json',
        'firecrawl_output.json',
        'scraped_data.json'
    ]
    
    for file_path in firecrawl_files:
        if os.path.exists(file_path):
            print(f"✅ Found Firecrawl data: {file_path}")
            with open(file_path, 'r') as f:
                return json.load(f), file_path
    
    print("❌ No Firecrawl data files found!")
    return None, None

def integrate_firecrawl_data(current_data, firecrawl_data, force_update=False):
    """Integrate Firecrawl data into education_faq.json"""
    print("🔗 Integrating Firecrawl data...")
    
    if not force_update:
        is_integrated, _ = check_firecrawl_integration()
        if is_integrated:
            print("⚠️  Firecrawl data appears to already be integrated.")
            response = input("Do you want to force re-integration? (y/N): ")
            if response.lower() != 'y':
                return current_data, False
    
    # Create firecrawl_integrated category if it doesn't exist
    if 'firecrawl_integrated' not in current_data:
        current_data['firecrawl_integrated'] = {}
    
    # Process Firecrawl data
    total_integrated = 0
    
    for main_category, subcategories in firecrawl_data.items():
        if isinstance(subcategories, dict):
            for subcat, items in subcategories.items():
                if isinstance(items, list):
                    # Create the integrated category path
                    integrated_key = f"web_scraped_{subcat}"
                    
                    # Add metadata to each item
                    processed_items = []
                    for item in items:
                        if isinstance(item, dict) and 'question' in item and 'answer' in item:
                            processed_item = {
                                **item,
                                'source': 'firecrawl_web_scraping',
                                'integrated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'original_category': f"{main_category}.{subcat}"
                            }
                            # Ensure chunk_id exists
                            if 'chunk_id' not in processed_item:
                                processed_item['chunk_id'] = str(uuid.uuid4())
                            
                            processed_items.append(processed_item)
                            total_integrated += 1
                    
                    if processed_items:
                        current_data['firecrawl_integrated'][integrated_key] = processed_items
                        print(f"  ✅ Integrated {len(processed_items)} items to {integrated_key}")
    
    print(f"🎉 Successfully integrated {total_integrated} Firecrawl entries!")
    return current_data, True

def save_integrated_data(data):
    """Save the integrated data back to the FAQ file"""
    print("💾 Saving integrated data...")
    
    faq_path = 'data/documents/education_faq.json'
    
    # Create backup
    backup_path = f"{faq_path}.backup_{int(time.time())}"
    if os.path.exists(faq_path):
        os.rename(faq_path, backup_path)
        print(f"📦 Created backup: {backup_path}")
    
    # Save new data
    with open(faq_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved integrated data to {faq_path}")

def reinitialize_rag_system():
    """Reinitialize the RAG system with the updated data"""
    print("🔄 Reinitializing RAG system...")
    
    try:
        # Initialize RAG system
        rag = RAGSystem()
        
        # Load the updated documents
        success = rag.load_documents('data/documents/education_faq.json')
        
        if success:
            print("✅ RAG system reinitialized successfully!")
            
            # Test with some queries
            test_queries = [
                "What is KIEC's success rate?",
                "How many universities does KIEC partner with?",
                "What countries does KIEC cover?",
                "Tell me about KIEC's experience"
            ]
            
            print("\n🧪 Testing RAG system with integrated data:")
            for query in test_queries:
                results = rag.search(query, k=1)
                if results:
                    result = results[0]
                    print(f"✅ Query: '{query}'")
                    print(f"   Score: {result['score']:.3f}")
                    print(f"   Answer: {result['answer'][:100]}...")
                    print(f"   Source: {result.get('source', 'N/A')}")
                    print()
                else:
                    print(f"❌ No results for: '{query}'")
            
            return True
        else:
            print("❌ Failed to reinitialize RAG system")
            return False
            
    except Exception as e:
        print(f"❌ Error reinitializing RAG system: {e}")
        return False

def verify_integration():
    """Verify the integration was successful"""
    print("🔍 Verifying integration...")
    
    # Check file size and structure
    faq_path = 'data/documents/education_faq.json'
    if os.path.exists(faq_path):
        file_size = os.path.getsize(faq_path)
        print(f"📊 FAQ file size: {file_size:,} bytes")
        
        with open(faq_path, 'r') as f:
            data = json.load(f)
        
        # Count total entries
        total_entries = 0
        firecrawl_entries = 0
        
        for category, subcategories in data.items():
            if isinstance(subcategories, dict):
                for subcat, items in subcategories.items():
                    if isinstance(items, list):
                        total_entries += len(items)
                        if 'firecrawl' in category.lower() or 'web_scraped' in subcat.lower():
                            firecrawl_entries += len(items)
        
        print(f"📈 Total FAQ entries: {total_entries}")
        print(f"🌐 Firecrawl entries: {firecrawl_entries}")
        print(f"📋 Categories: {list(data.keys())}")
        
        if firecrawl_entries > 0:
            print("✅ Firecrawl integration verified successfully!")
            return True
        else:
            print("❌ No Firecrawl entries found after integration")
            return False
    else:
        print("❌ FAQ file not found")
        return False

def main():
    """Main integration function"""
    print("🚀 Firecrawl Data Integration Script")
    print("=" * 50)
    
    # Step 1: Check current status
    is_integrated, current_data = check_firecrawl_integration()
    
    # Step 2: Load Firecrawl data
    firecrawl_data, firecrawl_file = load_firecrawl_data()
    
    if not firecrawl_data:
        print("❌ Cannot proceed without Firecrawl data")
        return False
    
    print(f"📊 Loaded Firecrawl data from: {firecrawl_file}")
    
    # Count items in Firecrawl data
    firecrawl_count = 0
    for category, subcategories in firecrawl_data.items():
        if isinstance(subcategories, dict):
            for subcat, items in subcategories.items():
                if isinstance(items, list):
                    firecrawl_count += len(items)
    
    print(f"📈 Firecrawl data contains: {firecrawl_count} Q&A pairs")
    
    # Step 3: Integrate data
    if not is_integrated or input("Force re-integration? (y/N): ").lower() == 'y':
        integrated_data, success = integrate_firecrawl_data(current_data, firecrawl_data, force_update=True)
        
        if success:
            # Step 4: Save integrated data
            save_integrated_data(integrated_data)
            
            # Step 5: Reinitialize RAG system
            rag_success = reinitialize_rag_system()
            
            # Step 6: Verify integration
            if rag_success:
                verify_success = verify_integration()
                
                if verify_success:
                    print("\n🎉 INTEGRATION COMPLETE!")
                    print("✅ Firecrawl data successfully integrated")
                    print("✅ RAG system reinitialized")
                    print("✅ Vector database updated")
                    print("✅ System ready for testing")
                    return True
                else:
                    print("\n❌ Integration verification failed")
                    return False
            else:
                print("\n❌ RAG system reinitialization failed")
                return False
        else:
            print("\n❌ Data integration failed")
            return False
    else:
        print("⏭️  Skipping integration - data already integrated")
        
        # Still test RAG system
        rag_success = reinitialize_rag_system()
        return rag_success

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Start your application: python app.py")
        print("2. Test Firecrawl queries like:")
        print("   - 'What is KIEC's success rate?'")
        print("   - 'How many universities does KIEC partner with?'")
        print("   - 'Tell me about KIEC's services'")
        print("3. Check the agent dashboard and human handoff")
    else:
        print("\n❌ Integration failed. Please check the errors above.")
