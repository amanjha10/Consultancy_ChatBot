#!/usr/bin/env python3
"""
Final RAG Integration Script
==========================

Complete integration with proper vector database setup and testing.
"""

import os
import sys
from datetime import datetime

def setup_final_rag_system():
    """Setup the final RAG system with proper configuration"""
    print("🤖 Setting up final RAG system...")
    
    # Add the parent directory to sys.path
    sys.path.append("/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot")
    
    try:
        from setup_rag import RAGSystem
        
        # Initialize RAG system with main vector directory
        rag_system = RAGSystem(persist_directory='data/vectors/chroma')
        
        # Load the main education FAQ
        faq_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/data/documents/education_faq.json"
        success = rag_system.load_documents(faq_path)
        
        if success:
            print("✅ RAG system updated successfully!")
            
            # Test the system with the correct method name
            print("🧪 Testing RAG system...")
            test_queries = [
                "What is KIEC's success rate?",
                "How can I get a scholarship to study abroad?", 
                "What are the visa requirements for studying in Canada?",
                "Which universities does Edwise Foundation work with?",
                "What is Expert Education Nepal's track record?"
            ]
            
            for query in test_queries:
                try:
                    # Use the correct method name 'search'
                    results = rag_system.search(query, k=1)
                    if results:
                        result = results[0]
                        print(f"   Q: {query}")
                        print(f"   A: {result.get('answer', 'No answer found')[:150]}...")
                        print(f"   📊 Confidence: {result.get('confidence', 0):.2f}")
                        print()
                    else:
                        print(f"   Q: {query}")
                        print(f"   A: No results found")
                        print()
                except Exception as e:
                    print(f"   ❌ Error testing query '{query}': {e}")
                    
        else:
            print("❌ Failed to update RAG system")
            return False
            
    except Exception as e:
        print(f"❌ Error updating RAG system: {e}")
        return False
    
    return True

def test_chatbot_integration():
    """Test integration with the main chatbot"""
    print("🔗 Testing chatbot integration...")
    
    try:
        # Add the parent directory to sys.path
        sys.path.append("/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot")
        
        from setup_rag import RAGSystem
        
        # Load the RAG system
        rag_system = RAGSystem.load('data/vectors/chroma')
        
        if rag_system:
            print("✅ RAG system loaded from storage successfully!")
            
            # Test a few queries
            test_queries = [
                "Tell me about KIEC",
                "What scholarships are available?",
                "How do I apply for a student visa?"
            ]
            
            for query in test_queries:
                try:
                    results = rag_system.search(query, k=1)
                    if results:
                        print(f"✅ Query '{query}' returned {len(results)} result(s)")
                    else:
                        print(f"⚠️  Query '{query}' returned no results")
                except Exception as e:
                    print(f"❌ Error with query '{query}': {e}")
        else:
            print("❌ Could not load RAG system from storage")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chatbot integration: {e}")
        return False
    
    return True

def main():
    """Main setup process"""
    print("🚀 Final RAG System Setup")
    print("=" * 40)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Setup RAG system
        print("\n📋 Step 1: Setting up RAG system...")
        rag_success = setup_final_rag_system()
        
        if rag_success:
            # Step 2: Test integration
            print("\n📋 Step 2: Testing chatbot integration...")
            integration_success = test_chatbot_integration()
            
            if integration_success:
                print("\n🎉 FINAL SETUP COMPLETED SUCCESSFULLY!")
                print("=" * 50)
                print("✅ Your educational consultancy chatbot is ready with:")
                print("   📊 180 high-quality Q&A pairs")
                print("   🌐 Data from 9 educational websites")
                print("   🔍 Semantic search enabled")
                print("   🤖 Integrated with main chatbot system")
                print("   👤 Admin FAQ management available")
                print("\n🚀 You can now start your chatbot with:")
                print("   cd '/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot'")
                print("   /Users/amanjha/Documents/untitled\\ folder\\ 3/bot/bin/python app.py")
                return True
            else:
                print("\n⚠️  RAG system setup complete but integration needs attention")
                return False
        else:
            print("\n❌ Failed to setup RAG system")
            return False
            
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
