"""
Data Processor Module
====================

Handles data processing, formatting, and output generation for Q&A pairs.
Converts Q&A pairs to the required JSON format and manages file operations.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import logging

try:
    from .qa_generator import QAPair
except ImportError:
    from qa_generator import QAPair

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Processes and formats Q&A data for output
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize data processor
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def qa_pairs_to_json_format(self, qa_pairs: List[QAPair]) -> Dict[str, Any]:
        """
        Convert Q&A pairs to the required JSON format
        
        Args:
            qa_pairs: List of QAPair objects
            
        Returns:
            Dictionary in the required JSON format
        """
        # Group Q&A pairs by category
        categorized_data = defaultdict(lambda: defaultdict(list))
        
        for qa_pair in qa_pairs:
            # Convert QAPair to dictionary format
            qa_dict = {
                "question": qa_pair.question,
                "answer": qa_pair.answer,
                "section": qa_pair.section,
                "page": qa_pair.page,
                "document": qa_pair.document,
                "chunk_id": qa_pair.chunk_id
            }
            
            # Determine subcategory based on section or content
            subcategory = self._determine_subcategory(qa_pair)
            
            # Add to categorized data
            categorized_data[qa_pair.category][subcategory].append(qa_dict)
        
        # Convert defaultdict to regular dict for JSON serialization
        output_data = {}
        for category, subcategories in categorized_data.items():
            output_data[category] = dict(subcategories)
        
        return output_data
    
    def _determine_subcategory(self, qa_pair: QAPair) -> str:
        """
        Determine subcategory based on Q&A content
        
        Args:
            qa_pair: QAPair object
            
        Returns:
            Subcategory name
        """
        section_lower = qa_pair.section.lower()
        question_lower = qa_pair.question.lower()
        answer_lower = qa_pair.answer.lower()
        
        # Map sections to subcategories
        subcategory_mapping = {
            # General queries subcategories
            'study_abroad_basics': ['getting started', 'basics', 'overview', 'introduction', 'general'],
            'process_information': ['process', 'steps', 'procedure', 'how to'],
            'cost_information': ['cost', 'fee', 'expense', 'budget', 'financial'],
            
            # Visa information subcategories  
            'visa_requirements': ['requirement', 'visa', 'documentation', 'document'],
            'application_process': ['application', 'apply', 'process'],
            
            # Language requirements subcategories
            'english_speaking_countries': ['ielts', 'toefl', 'english', 'language test'],
            'non_english_countries': ['german', 'french', 'local language', 'native'],
            
            # Scholarships subcategories
            'global_opportunities': ['international', 'global', 'worldwide', 'major'],
            'country_specific': ['country', 'national', 'government', 'local'],
            'merit_based': ['merit', 'academic', 'excellence'],
            'need_based': ['need', 'financial need', 'income'],
            
            # Accommodation subcategories
            'university_housing': ['dormitory', 'campus', 'university housing', 'residence hall'],
            'private_housing': ['apartment', 'private', 'off-campus', 'rental'],
            'homestay': ['homestay', 'host family', 'family'],
            
            # Career prospects subcategories
            'post_study_work': ['work permit', 'employment', 'job', 'career'],
            'job_markets': ['job market', 'opportunities', 'employment rate'],
            
            # Application process subcategories
            'admission_requirements': ['admission', 'requirement', 'eligibility'],
            'documents': ['document', 'transcript', 'certificate', 'letter'],
            'deadlines': ['deadline', 'timeline', 'when to apply'],
        }
        
        # Check for matches
        combined_text = f"{section_lower} {question_lower} {answer_lower}"
        
        for subcategory, keywords in subcategory_mapping.items():
            if any(keyword in combined_text for keyword in keywords):
                return subcategory
        
        # Default subcategories for each main category
        default_subcategories = {
            'general_queries': 'study_abroad_basics',
            'visa_information': 'visa_requirements', 
            'language_requirements': 'english_speaking_countries',
            'scholarships': 'global_opportunities',
            'accommodation': 'university_housing',
            'career_prospects': 'post_study_work',
            'application_process': 'admission_requirements',
            'costs_and_finances': 'cost_information',
            'custom_entries': 'custom_entries'
        }
        
        return default_subcategories.get(qa_pair.category, 'other')
    
    def save_qa_data(self, qa_pairs: List[QAPair], filename: Optional[str] = None) -> str:
        """
        Save Q&A pairs to JSON file
        
        Args:
            qa_pairs: List of QAPair objects
            filename: Output filename (auto-generated if not provided)
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"firecrawl_qa_data_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert to JSON format
        json_data = self.qa_pairs_to_json_format(qa_pairs)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Saved {len(qa_pairs)} Q&A pairs to {filepath}")
        return filepath
    
    def merge_with_existing_data(self, new_qa_pairs: List[QAPair], existing_file: str) -> str:
        """
        Merge new Q&A pairs with existing data file
        
        Args:
            new_qa_pairs: New Q&A pairs to add
            existing_file: Path to existing JSON file
            
        Returns:
            Path to updated file
        """
        try:
            # Load existing data
            with open(existing_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            # Convert new Q&A pairs to JSON format
            new_data = self.qa_pairs_to_json_format(new_qa_pairs)
            
            # Merge data
            merged_data = self._merge_json_data(existing_data, new_data)
            
            # Save merged data
            with open(existing_file, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Merged {len(new_qa_pairs)} new Q&A pairs with existing data in {existing_file}")
            return existing_file
            
        except Exception as e:
            logger.error(f"Error merging data: {e}")
            # Fallback: save as new file
            return self.save_qa_data(new_qa_pairs)
    
    def _merge_json_data(self, existing_data: Dict, new_data: Dict) -> Dict:
        """
        Merge two JSON data structures
        
        Args:
            existing_data: Existing Q&A data
            new_data: New Q&A data to merge
            
        Returns:
            Merged data dictionary
        """
        merged = existing_data.copy()
        
        for category, subcategories in new_data.items():
            if category not in merged:
                merged[category] = {}
            
            for subcategory, qa_list in subcategories.items():
                if subcategory not in merged[category]:
                    merged[category][subcategory] = []
                
                # Add new Q&A pairs (avoid duplicates based on question)
                existing_questions = {qa['question'] for qa in merged[category][subcategory]}
                
                for qa in qa_list:
                    if qa['question'] not in existing_questions:
                        merged[category][subcategory].append(qa)
        
        return merged
    
    def generate_summary_report(self, qa_pairs: List[QAPair], crawl_results: List[Any]) -> Dict[str, Any]:
        """
        Generate summary report of the crawling and Q&A generation process
        
        Args:
            qa_pairs: Generated Q&A pairs
            crawl_results: Crawl results from Firecrawl
            
        Returns:
            Summary report dictionary
        """
        # Count Q&A pairs by category
        category_counts = defaultdict(int)
        confidence_scores = []
        
        for qa_pair in qa_pairs:
            category_counts[qa_pair.category] += 1
            confidence_scores.append(qa_pair.confidence_score)
        
        # Calculate statistics
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Count successful crawls
        successful_crawls = sum(1 for result in crawl_results if hasattr(result, 'success') and result.success)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'crawl_statistics': {
                'total_urls_processed': len(crawl_results),
                'successful_crawls': successful_crawls,
                'failed_crawls': len(crawl_results) - successful_crawls,
                'success_rate': f"{(successful_crawls/len(crawl_results)*100):.1f}%" if crawl_results else "0%"
            },
            'qa_generation_statistics': {
                'total_qa_pairs': len(qa_pairs),
                'average_confidence_score': round(avg_confidence, 3),
                'qa_pairs_by_category': dict(category_counts),
                'high_confidence_pairs': sum(1 for score in confidence_scores if score > 0.7),
                'medium_confidence_pairs': sum(1 for score in confidence_scores if 0.4 <= score <= 0.7),
                'low_confidence_pairs': sum(1 for score in confidence_scores if score < 0.4)
            },
            'sources_processed': [
                result.url for result in crawl_results 
                if hasattr(result, 'success') and result.success
            ]
        }
        
        return report
    
    def save_summary_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """
        Save summary report to file
        
        Args:
            report: Summary report dictionary
            filename: Output filename (auto-generated if not provided)
            
        Returns:
            Path to saved report file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"firecrawl_summary_report_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Saved summary report to {filepath}")
        return filepath
    
    def export_to_csv(self, qa_pairs: List[QAPair], filename: Optional[str] = None) -> str:
        """
        Export Q&A pairs to CSV format
        
        Args:
            qa_pairs: List of QAPair objects
            filename: Output filename (auto-generated if not provided)
            
        Returns:
            Path to saved CSV file
        """
        import csv
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"firecrawl_qa_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Question', 'Answer', 'Section', 'Category', 
                'Document', 'Page', 'Chunk_ID', 'Confidence_Score'
            ])
            
            # Write data
            for qa_pair in qa_pairs:
                writer.writerow([
                    qa_pair.question,
                    qa_pair.answer,
                    qa_pair.section,
                    qa_pair.category,
                    qa_pair.document,
                    qa_pair.page,
                    qa_pair.chunk_id,
                    qa_pair.confidence_score
                ])
        
        logger.info(f"Exported {len(qa_pairs)} Q&A pairs to CSV: {filepath}")
        return filepath
