"""
Q&A Generator Module
===================

Generates structured Q&A pairs from crawled content using Gemini AI.
Handles content chunking, prompt engineering, and response parsing.
"""

import os
import json
import uuid
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

@dataclass 
class QAPair:
    """Data class for Q&A pairs"""
    question: str
    answer: str
    section: str
    page: int
    document: str
    chunk_id: str
    category: str
    confidence_score: float = 0.0

class QAGenerator:
    """
    Generates Q&A pairs from content using Gemini AI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Q&A generator with Gemini API
        
        Args:
            api_key: Gemini API key (if not provided, loads from .env)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in .env file")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Content categories for classification
        self.categories = {
            'general_queries': [
                'study abroad basics', 'getting started', 'overview', 'introduction',
                'general information', 'about studying abroad'
            ],
            'visa_information': [
                'visa', 'immigration', 'student visa', 'visa requirements', 
                'documentation', 'passport', 'entry requirements'
            ],
            'language_requirements': [
                'ielts', 'toefl', 'duolingo', 'english test', 'language proficiency',
                'english requirements', 'language certification'
            ],
            'scholarships': [
                'scholarship', 'funding', 'financial aid', 'grants', 'bursary',
                'financial assistance', 'merit scholarship', 'need-based aid'
            ],
            'accommodation': [
                'housing', 'accommodation', 'dormitory', 'residence', 'homestay',
                'student housing', 'living arrangements'
            ],
            'career_prospects': [
                'career', 'job opportunities', 'employment', 'work permit',
                'post-study work', 'job market', 'career prospects'
            ],
            'application_process': [
                'application', 'admission', 'apply', 'application process',
                'admission requirements', 'how to apply'
            ],
            'costs_and_finances': [
                'cost', 'tuition', 'fees', 'expenses', 'budget', 'financial planning',
                'cost of living', 'education cost'
            ]
        }
        
        self.chunk_size = 3000  # Maximum characters per chunk
        self.max_qa_pairs_per_chunk = 8  # Maximum Q&A pairs to generate per chunk
    
    def chunk_content(self, content: str, chunk_size: Optional[int] = None) -> List[str]:
        """
        Split content into manageable chunks for processing
        
        Args:
            content: Text content to chunk
            chunk_size: Size of each chunk in characters
            
        Returns:
            List of content chunks
        """
        chunk_size = chunk_size or self.chunk_size
        
        # Split by paragraphs first, then by sentences if needed
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If chunks are still too large, split by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                sentences = re.split(r'(?<=[.!?])\s+', chunk)
                sub_chunk = ""
                for sentence in sentences:
                    if len(sub_chunk) + len(sentence) <= chunk_size:
                        sub_chunk += sentence + " "
                    else:
                        if sub_chunk.strip():
                            final_chunks.append(sub_chunk.strip())
                        sub_chunk = sentence + " "
                if sub_chunk.strip():
                    final_chunks.append(sub_chunk.strip())
        
        return final_chunks
    
    def generate_qa_prompt(self, content: str, source_info: Dict[str, str]) -> str:
        """
        Generate prompt for Q&A extraction
        
        Args:
            content: Content chunk to process
            source_info: Information about the source (title, URL, etc.)
            
        Returns:
            Formatted prompt for Gemini
        """
        return f"""
You are an expert educational consultant who specializes in study abroad guidance. 

Analyze the following content from {source_info.get('title', 'Unknown Source')} ({source_info.get('url', 'Unknown URL')}) and extract valuable information to create Question-Answer pairs.

CONTENT TO ANALYZE:
{content}

INSTRUCTIONS:
1. Extract {self.max_qa_pairs_per_chunk} high-quality, specific Question-Answer pairs from this content
2. Focus on practical, actionable information that students would find valuable
3. Ensure questions are clear and answers are comprehensive but concise
4. Infer appropriate section titles based on the content topic
5. Cover different aspects: requirements, processes, costs, opportunities, etc.

STRICT OUTPUT FORMAT:
Return ONLY a valid JSON array with this exact structure:

[
  {{
    "question": "What are the English language requirements for studying in the UK?",
    "answer": "For UK universities, you typically need IELTS 6.0-7.0 for undergraduate programs and 6.5-7.5 for postgraduate programs. TOEFL scores of 80-100 (undergraduate) and 90-110 (postgraduate) are also accepted. Some universities may accept Duolingo English Test.",
    "section": "Language Requirements",
    "confidence_score": 0.9
  }},
  {{
    "question": "How much does it cost to study in Germany?",
    "answer": "Public universities in Germany charge no tuition fees for EU and international students, only semester fees of €150-350. Private universities charge €20,000-40,000 per year. Living costs range from €800-1,200 per month depending on the city.",
    "section": "Cost Information", 
    "confidence_score": 0.85
  }}
]

QUALITY REQUIREMENTS:
- Questions must be specific and relevant to study abroad
- Answers must be factual and detailed
- Include numbers, requirements, and specific information when available
- Confidence score should reflect how certain you are about the information (0.0-1.0)
- Section should be descriptive and relevant to the topic

Return ONLY the JSON array, no other text or formatting.
"""
    
    def parse_gemini_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse Gemini's JSON response and handle potential formatting issues
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            List of parsed Q&A dictionaries
        """
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code block formatting if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            qa_data = json.loads(cleaned_text)
            
            # Ensure it's a list
            if not isinstance(qa_data, list):
                logger.warning("Response is not a list, wrapping in list")
                qa_data = [qa_data]
            
            return qa_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            
            # Try to extract JSON from the response using regex
            json_pattern = r'\[.*?\]'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            if matches:
                try:
                    return json.loads(matches[0])
                except:
                    pass
            
            return []
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return []
    
    def categorize_qa(self, qa_pair: Dict[str, Any]) -> str:
        """
        Categorize Q&A pair based on content
        
        Args:
            qa_pair: Q&A pair dictionary
            
        Returns:
            Category name
        """
        question_lower = qa_pair.get('question', '').lower()
        answer_lower = qa_pair.get('answer', '').lower()
        section_lower = qa_pair.get('section', '').lower()
        
        combined_text = f"{question_lower} {answer_lower} {section_lower}"
        
        # Score each category
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'custom_entries' if no match
        if category_scores:
            return max(category_scores, key=category_scores.get)
        else:
            return 'custom_entries'
    
    def generate_qa_pairs(self, content: str, source_info: Dict[str, str]) -> List[QAPair]:
        """
        Generate Q&A pairs from content using Gemini
        
        Args:
            content: Text content to process
            source_info: Source information (title, URL, etc.)
            
        Returns:
            List of QAPair objects
        """
        if not content.strip():
            logger.warning("Empty content provided")
            return []
        
        qa_pairs = []
        
        # Chunk the content
        chunks = self.chunk_content(content)
        logger.info(f"Processing {len(chunks)} content chunks")
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{len(chunks)}")
            
            try:
                # Generate prompt
                prompt = self.generate_qa_prompt(chunk, source_info)
                
                # Get response from Gemini
                response = self.model.generate_content(prompt)
                
                if response.text:
                    # Parse the response
                    qa_data = self.parse_gemini_response(response.text)
                    
                    # Convert to QAPair objects
                    for qa_dict in qa_data:
                        try:
                            # Categorize the Q&A pair
                            category = self.categorize_qa(qa_dict)
                            
                            qa_pair = QAPair(
                                question=qa_dict.get('question', '').strip(),
                                answer=qa_dict.get('answer', '').strip(),
                                section=qa_dict.get('section', 'General Information').strip(),
                                page=i-1,  # Chunk number as page
                                document=source_info.get('title', 'Unknown Source'),
                                chunk_id=str(uuid.uuid4()),
                                category=category,
                                confidence_score=qa_dict.get('confidence_score', 0.5)
                            )
                            
                            # Validate Q&A pair
                            if qa_pair.question and qa_pair.answer:
                                qa_pairs.append(qa_pair)
                            else:
                                logger.warning("Skipping invalid Q&A pair (empty question or answer)")
                                
                        except Exception as e:
                            logger.error(f"Error creating QAPair object: {e}")
                            continue
                else:
                    logger.warning(f"No response text from Gemini for chunk {i}")
                    
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {e}")
                continue
        
        logger.info(f"Generated {len(qa_pairs)} Q&A pairs from {len(chunks)} chunks")
        return qa_pairs
    
    def filter_qa_pairs(self, qa_pairs: List[QAPair], min_confidence: float = 0.3) -> List[QAPair]:
        """
        Filter Q&A pairs based on quality criteria
        
        Args:
            qa_pairs: List of QAPair objects
            min_confidence: Minimum confidence score to keep
            
        Returns:
            Filtered list of QAPair objects
        """
        filtered_pairs = []
        
        for qa_pair in qa_pairs:
            # Check confidence score
            if qa_pair.confidence_score < min_confidence:
                logger.debug(f"Filtering out low confidence Q&A: {qa_pair.question[:50]}...")
                continue
            
            # Check minimum length requirements
            if len(qa_pair.question) < 10 or len(qa_pair.answer) < 20:
                logger.debug(f"Filtering out short Q&A: {qa_pair.question[:50]}...")
                continue
            
            # Check for generic/useless questions
            generic_patterns = [
                r'^what is.*\?$',
                r'^how.*\?$',
                r'^when.*\?$',
                r'^where.*\?$'
            ]
            
            question_lower = qa_pair.question.lower()
            is_generic = any(re.match(pattern, question_lower) and len(question_lower) < 30 
                           for pattern in generic_patterns)
            
            if is_generic:
                logger.debug(f"Filtering out generic question: {qa_pair.question}")
                continue
            
            filtered_pairs.append(qa_pair)
        
        logger.info(f"Filtered {len(qa_pairs)} Q&A pairs down to {len(filtered_pairs)} high-quality pairs")
        return filtered_pairs
