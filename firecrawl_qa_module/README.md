# Firecrawl Q&A Module

A comprehensive Python module for crawling consultancy websites and generating structured Q&A pairs using Firecrawl API and Google Gemini AI.

## 🌟 Features

- **Web Scraping**: Uses Firecrawl API to crawl educational consultancy websites
- **AI-Powered Q&A Generation**: Leverages Google Gemini AI to extract and generate high-quality Q&A pairs
- **Structured Output**: Organizes Q&A pairs into categories (visa, scholarships, general queries, etc.)
- **Batch Processing**: Handles multiple URLs with rate limiting and retry mechanisms
- **Data Export**: Supports JSON and CSV export formats
- **Comprehensive Reporting**: Generates detailed summary reports with statistics

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in your project directory with your API keys:

```env
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Basic Usage

```python
from firecrawl_qa_module import FirecrawlQAModule

# Initialize the module
module = FirecrawlQAModule(output_dir="my_output")

# Crawl a single URL
result = module.crawl_single_url("https://educationusa.state.gov")

# Process multiple URLs
urls = [
    "https://kiec.edu.np",
    "https://edwisefoundation.com",
    "https://www.daad.de/en"
]

results = module.crawl_and_generate_qa(urls, min_confidence=0.4)

print(f"Generated {len(results['qa_pairs'])} Q&A pairs")
```

### 4. Run Examples

Try the example script:

```bash
python example_usage.py
```

## 📊 Output Format

The module generates Q&A pairs in this structured JSON format:

```json
{
  "general_queries": {
    "study_abroad_basics": [
      {
        "question": "What are the English language requirements for studying in the UK?",
        "answer": "For UK universities, you typically need IELTS 6.0-7.0 for undergraduate programs...",
        "section": "Language Requirements",
        "page": 0,
        "document": "UK Study Guide",
        "chunk_id": "uuid-here"
      }
    ]
  },
  "scholarships": {
    "global_opportunities": [
      {
        "question": "What are the major international scholarships available?",
        "answer": "Major scholarships include Fulbright, Chevening, DAAD, Erasmus Mundus...",
        "section": "Financial Aid",
        "page": 1,
        "document": "Scholarship Guide",
        "chunk_id": "uuid-here"
      }
    ]
  }
}
```

## 🎯 Supported Categories

- **general_queries**: Basic study abroad information
- **visa_information**: Visa requirements and processes
- **language_requirements**: IELTS, TOEFL, and other language tests
- **scholarships**: Funding opportunities and financial aid
- **accommodation**: Housing options for international students
- **career_prospects**: Job opportunities and post-study work
- **application_process**: Admission requirements and procedures
- **costs_and_finances**: Tuition fees and living expenses

## 🌐 Target Websites

### Nepal-based Consultancies
- https://kiec.edu.np
- https://edwisefoundation.com
- https://experteducation.com/nepal/
- https://www.aeccglobal.com.np
- https://niec.edu.np

### Official Government Portals
- https://educationusa.state.gov
- https://www.studyinaustralia.gov.au
- https://www.ukcisa.org.uk
- https://www.daad.de/en
- https://www.educanada.ca

## 📚 Advanced Usage

### Predefined URL Sets

```python
# Process all consultancy URLs
results = module.crawl_predefined_urls(url_set="consultancy")

# Process government education portals
results = module.crawl_predefined_urls(url_set="government")

# Process all predefined URLs
results = module.crawl_predefined_urls(url_set="all")
```

### Merge with Existing Data

```python
# Add new Q&A pairs to existing data file
new_urls = ["https://new-consultancy.com"]
updated_file = module.update_existing_qa_data(
    urls=new_urls,
    existing_file="existing_qa_data.json"
)
```

### Custom Configuration

```python
# Initialize with custom settings
module = FirecrawlQAModule(
    firecrawl_api_key="your_key",
    gemini_api_key="your_key", 
    output_dir="custom_output"
)

# Adjust confidence threshold
results = module.crawl_and_generate_qa(
    urls=urls,
    min_confidence=0.6  # Higher threshold for better quality
)
```

## 📁 Output Files

The module generates several output files:

1. **Q&A Data**: `firecrawl_qa_data_YYYYMMDD_HHMMSS.json`
2. **CSV Export**: `firecrawl_qa_data_YYYYMMDD_HHMMSS.csv`
3. **Summary Report**: `firecrawl_summary_report_YYYYMMDD_HHMMSS.json`
4. **Crawl Results**: `crawl_results_YYYYMMDD_HHMMSS.json` (if enabled)

## 🔧 Configuration Options

### Crawler Settings
- `rate_limit_delay`: Delay between requests (default: 2 seconds)
- `max_retries`: Maximum retry attempts (default: 3)
- `timeout`: Request timeout (default: 30 seconds)

### Q&A Generator Settings
- `chunk_size`: Maximum characters per content chunk (default: 3000)
- `max_qa_pairs_per_chunk`: Maximum Q&A pairs per chunk (default: 8)
- `min_confidence`: Minimum confidence score for filtering (default: 0.3)

## 📈 Statistics and Reporting

Get module statistics:

```python
stats = module.get_statistics()
print(f"Supported categories: {stats['supported_categories']}")
print(f"Available URL sets: {stats['predefined_url_sets']}")
```

## 🚨 Error Handling

The module includes comprehensive error handling:

- **Network errors**: Automatic retries with exponential backoff
- **API rate limits**: Built-in rate limiting
- **Content parsing errors**: Graceful failure with logging
- **Invalid responses**: Validation and filtering

## 📝 Logging

All operations are logged with different levels:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Log files are automatically created in the working directory.

## 🤝 Contributing

This module is part of the EduConsult chatbot system. For issues or improvements:

1. Check the logs for detailed error information
2. Verify API keys are correctly set in `.env`
3. Ensure all dependencies are installed
4. Test with a single URL first before batch processing

## 📄 License

This module is part of the EduConsult project. Please refer to the main project license.

---

**Happy Crawling! 🕷️✨**
