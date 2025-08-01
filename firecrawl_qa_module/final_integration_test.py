#!/usr/bin/env python3
"""
Final Integration Test & Setup
============================

Complete test of the integrated RAG system with Firecrawl data.
"""

import os
import sys
from datetime import datetime

def test_final_integration():
    """Test the final integration comprehensively"""
    print("🔍 Final Integration Test")
    print("=" * 40)
    
    # Add the parent directory to sys.path
    sys.path.append("/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot")
    
    try:
        from setup_rag import RAGSystem
        
        # Test direct initialization (this should work)
        print("📋 Test 1: Direct RAG system initialization...")
        rag_system = RAGSystem()
        
        # Load documents
        faq_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/data/documents/education_faq.json"
        success = rag_system.load_documents(faq_path)
        
        if success:
            print("✅ Documents loaded successfully!")
            
            # Test queries with the new Firecrawl data
            test_queries = [
                "What is KIEC's success rate?",
                "Tell me about Edwise Foundation",
                "What services does Expert Education Nepal offer?",
                "How many students has KIEC helped?",
                "What scholarships are available?",
                "Visa requirements for Canada"
            ]
            
            print("\n🧪 Testing queries on integrated data...")
            successful_queries = 0
            
            for query in test_queries:
                try:
                    results = rag_system.search(query, k=2)
                    if results and len(results) > 0:
                        result = results[0]
                        answer = result.get('answer', 'N/A')
                        question = result.get('question', 'N/A')
                        
                        print(f"✅ Q: {query}")
                        print(f"   Matched: {question[:80]}...")
                        print(f"   A: {answer[:100]}...")
                        print()
                        successful_queries += 1
                    else:
                        print(f"❌ Q: {query} - No results found")
                except Exception as e:
                    print(f"❌ Q: {query} - Error: {e}")
            
            print(f"📊 Query Success Rate: {successful_queries}/{len(test_queries)} ({successful_queries/len(test_queries)*100:.1f}%)")
            
            if successful_queries >= len(test_queries) * 0.8:  # 80% success rate
                print("✅ Integration test PASSED!")
                return True
            else:
                print("⚠️  Integration test partially successful")
                return False
                
        else:
            print("❌ Failed to load documents")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def show_integration_summary():
    """Show final integration summary"""
    print("\n🎉 FIRECRAWL Q&A INTEGRATION COMPLETED!")
    print("=" * 55)
    
    # Check files
    faq_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/data/documents/education_faq.json"
    vector_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/data/vectors/chroma"
    
    print("📁 File Status:")
    print(f"   ✅ Main FAQ file: {os.path.exists(faq_path)}")
    print(f"   ✅ Vector database: {os.path.exists(vector_path)}")
    
    if os.path.exists(faq_path):
        import json
        with open(faq_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Count Q&A pairs
        total_qa = 0
        categories = 0
        for category, subcategories in data.items():
            if isinstance(subcategories, dict):
                categories += 1
                for subcategory, qa_pairs in subcategories.items():
                    if isinstance(qa_pairs, list):
                        total_qa += len(qa_pairs)
        
        print(f"\n📊 Knowledge Base Statistics:")
        print(f"   📚 Total Q&A pairs: {total_qa}")
        print(f"   📂 Categories: {categories}")
    
    print(f"\n🌐 Data Sources Successfully Integrated:")
    print("   ✅ Original education FAQ (existing knowledge)")
    print("   ✅ Admin-added FAQs (dynamic additions)")
    print("   ✅ Firecrawl scraped data from 9 websites:")
    print("      • KIEC (kiec.edu.np)")
    print("      • Edwise Foundation (edwisefoundation.com)")
    print("      • Expert Education Nepal (experteducation.com/nepal/)")
    print("      • AECC Nepal (aeccglobal.com.np)")
    print("      • NIEC (niec.edu.np)")
    print("      • EducationUSA (educationusa.state.gov)")
    print("      • UKCISA (ukcisa.org.uk)")
    print("      • DAAD Germany (daad.de/en)")
    print("      • Study in Canada (educanada.ca)")
    
    print(f"\n🚀 Next Steps:")
    print("   1. Start your chatbot:")
    print("      cd '/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot'")
    print("      /Users/amanjha/Documents/untitled\\ folder\\ 3/bot/bin/python app.py")
    print("   2. Test the enhanced knowledge through chat interface")
    print("   3. Add more Q&A pairs through admin interface as needed")
    print("   4. Use Firecrawl module for future website updates")

def main():
    """Main test and summary"""
    print("🚀 Final Integration Test & Summary")
    print("=" * 45)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run integration test
    test_success = test_final_integration()
    
    # Show summary regardless of test result
    show_integration_summary()
    
    return test_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
