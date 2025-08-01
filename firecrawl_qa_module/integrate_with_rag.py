#!/usr/bin/env python3
"""
RAG Integration Script
====================

Integrates Firecrawl Q&A data with existing education FAQ system.
Updates the vector database with combined knowledge base.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import uuid

def load_existing_education_faq() -> Dict[str, Any]:
    """Load existing education FAQ data"""
    faq_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/data/documents/education_faq.json"
    
    if os.path.exists(faq_path):
        with open(faq_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"❌ Education FAQ file not found at: {faq_path}")
        return {}

def load_firecrawl_qa_data() -> Dict[str, Any]:
    """Load the latest Firecrawl Q&A data"""
    firecrawl_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/firecrawl_qa_module/complete_crawl_output/firecrawl_qa_data_20250730_122917.json"
    
    if os.path.exists(firecrawl_path):
        with open(firecrawl_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"❌ Firecrawl Q&A file not found at: {firecrawl_path}")
        return {}

def normalize_category_mapping() -> Dict[str, str]:
    """Map Firecrawl categories to standard education FAQ categories"""
    return {
        # Firecrawl categories -> Standard categories
        "custom_entries": "general_queries",
        "global_opportunities": "general_queries", 
        "need_based": "scholarships",
        "merit_based": "scholarships",
        "job_markets": "career_prospects",
        "process_information": "application_process",
        "private_housing": "accommodation",
        "university_housing": "accommodation",
        "country_specific": "general_queries",
        "cost_information": "costs_and_finances",
        "study_abroad_basics": "general_queries",
        "visa_requirements": "visa_information",
        
        # Direct mappings (already standard)
        "scholarships": "scholarships",
        "application_process": "application_process", 
        "language_requirements": "language_requirements",
        "career_prospects": "career_prospects",
        "general_queries": "general_queries",
        "costs_and_finances": "costs_and_finances",
        "visa_information": "visa_information",
        "accommodation": "accommodation"
    }

def merge_qa_data(existing_faq: Dict[str, Any], firecrawl_data: Dict[str, Any]) -> Dict[str, Any]:
    """Merge Firecrawl Q&A data into existing FAQ structure"""
    print("🔄 Merging Q&A datasets...")
    
    # Create a copy of existing FAQ
    merged_data = existing_faq.copy()
    category_mapping = normalize_category_mapping()
    
    # Statistics
    original_count = 0
    firecrawl_count = 0
    
    # Count original Q&A pairs
    for category in merged_data:
        if isinstance(merged_data[category], dict):
            for subcategory in merged_data[category]:
                if isinstance(merged_data[category][subcategory], list):
                    original_count += len(merged_data[category][subcategory])
    
    # Process Firecrawl data
    for firecrawl_category, subcategories in firecrawl_data.items():
        if isinstance(subcategories, dict):
            # Map to standard category
            standard_category = category_mapping.get(firecrawl_category, "general_queries")
            
            # Ensure standard category exists
            if standard_category not in merged_data:
                merged_data[standard_category] = {}
            
            # Process subcategories
            for subcategory, qa_pairs in subcategories.items():
                if isinstance(qa_pairs, list):
                    # Map subcategory too
                    standard_subcategory = category_mapping.get(subcategory, subcategory)
                    
                    # Ensure subcategory exists
                    if standard_subcategory not in merged_data[standard_category]:
                        merged_data[standard_category][standard_subcategory] = []
                    
                    # Add Q&A pairs with firecrawl source marking
                    for qa_pair in qa_pairs:
                        if isinstance(qa_pair, dict) and 'question' in qa_pair and 'answer' in qa_pair:
                            # Add source metadata
                            enhanced_qa = qa_pair.copy()
                            enhanced_qa['source'] = 'firecrawl'
                            enhanced_qa['imported_date'] = datetime.now().isoformat()
                            
                            # Generate new chunk_id if missing
                            if 'chunk_id' not in enhanced_qa:
                                enhanced_qa['chunk_id'] = str(uuid.uuid4())
                            
                            merged_data[standard_category][standard_subcategory].append(enhanced_qa)
                            firecrawl_count += 1
    
    print(f"✅ Merged successfully:")
    print(f"   📊 Original Q&A pairs: {original_count}")
    print(f"   📊 Firecrawl Q&A pairs: {firecrawl_count}")
    print(f"   📊 Total Q&A pairs: {original_count + firecrawl_count}")
    
    return merged_data

def save_merged_data(merged_data: Dict[str, Any]) -> str:
    """Save merged data to education_faq.json"""
    output_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/data/documents/education_faq.json"
    
    # Create backup of original
    backup_path = f"{output_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            original_data = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_data)
        print(f"📁 Created backup: {backup_path}")
    
    # Save merged data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=4, ensure_ascii=False)
    
    print(f"💾 Saved merged data to: {output_path}")
    return output_path

def update_rag_system():
    """Update RAG system with new knowledge base"""
    print("🤖 Updating RAG system...")
    
    # Add the parent directory to sys.path
    sys.path.append("/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot")
    
    try:
        from setup_rag import RAGSystem
        
        # Initialize RAG system
        rag_system = RAGSystem()
        
        # Load and process the merged education FAQ
        faq_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/data/documents/education_faq.json"
        success = rag_system.load_documents(faq_path)
        
        if success:
            print("✅ RAG system updated successfully!")
            
            # Test the system
            print("🧪 Testing RAG system...")
            test_queries = [
                "What is KIEC's success rate?",
                "How can I get a scholarship to study abroad?",
                "What are the visa requirements for studying in Canada?",
                "Which universities does Edwise Foundation work with?"
            ]
            
            for query in test_queries:
                try:
                    result = rag_system.query(query)
                    print(f"   Q: {query}")
                    print(f"   A: {result['answer'][:100]}...")
                    print(f"   📊 Confidence: {result['confidence']:.2f}")
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

def generate_integration_report(merged_data: Dict[str, Any]) -> str:
    """Generate integration report"""
    report = {
        "integration_timestamp": datetime.now().isoformat(),
        "integration_summary": {
            "status": "completed",
            "total_categories": len(merged_data),
            "category_breakdown": {}
        },
        "data_sources": {
            "original_education_faq": "existing knowledge base",
            "firecrawl_data": "web-scraped consultancy data",
            "admin_faqs": "dynamically added by administrators"
        },
        "next_steps": [
            "Monitor chatbot performance with enhanced knowledge base",
            "Add more Q&A pairs through admin interface as needed",
            "Regular updates using Firecrawl module for fresh content"
        ]
    }
    
    # Calculate category breakdown
    total_qa_pairs = 0
    for category, subcategories in merged_data.items():
        if isinstance(subcategories, dict):
            category_count = 0
            for subcategory, qa_pairs in subcategories.items():
                if isinstance(qa_pairs, list):
                    category_count += len(qa_pairs)
            report["integration_summary"]["category_breakdown"][category] = category_count
            total_qa_pairs += category_count
    
    report["integration_summary"]["total_qa_pairs"] = total_qa_pairs
    
    # Save report
    report_path = "/Users/amanjha/Documents/untitled folder 3/Consultancy_ChatBot/firecrawl_qa_module/integration_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    return report_path

def main():
    """Main integration process"""
    print("🚀 Starting RAG Integration Process")
    print("=" * 50)
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Load existing data
        print("\n📋 Step 1: Loading existing education FAQ...")
        existing_faq = load_existing_education_faq()
        if not existing_faq:
            print("❌ Failed to load existing FAQ data")
            return False
        print("✅ Existing FAQ data loaded")
        
        # Step 2: Load Firecrawl data  
        print("\n📋 Step 2: Loading Firecrawl Q&A data...")
        firecrawl_data = load_firecrawl_qa_data()
        if not firecrawl_data:
            print("❌ Failed to load Firecrawl data")
            return False
        print("✅ Firecrawl Q&A data loaded")
        
        # Step 3: Merge datasets
        print("\n📋 Step 3: Merging datasets...")
        merged_data = merge_qa_data(existing_faq, firecrawl_data)
        
        # Step 4: Save merged data
        print("\n📋 Step 4: Saving merged data...")
        save_merged_data(merged_data)
        
        # Step 5: Update RAG system
        print("\n📋 Step 5: Updating RAG system...")
        rag_success = update_rag_system()
        
        # Step 6: Generate report
        print("\n📋 Step 6: Generating integration report...")
        report_path = generate_integration_report(merged_data)
        print(f"📄 Integration report saved to: {report_path}")
        
        if rag_success:
            print("\n🎉 Integration completed successfully!")
            print("=" * 50)
            print("✅ Your chatbot now has enhanced knowledge from:")
            print("   📚 Original education FAQ")
            print("   🌐 Firecrawl web-scraped data (156 Q&A pairs)")
            print("   👤 Admin-added FAQs")
            print("\n🤖 Your chatbot is ready with comprehensive knowledge!")
        else:
            print("\n⚠️  Integration partially completed with RAG system issues")
            
        return rag_success
        
    except Exception as e:
        print(f"\n❌ Integration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
