# CV Processor Module

**Project:** CVMatch - CV Processing & Text Extraction (Task 1)
**Programmers:** Santiago Cardenas and Amel Sunil
**First Version:** 2025-02-27

## Overview

The `cv_processor` package extracts text from CV/resume files (PDF, DOCX, TXT) and uses the **OpenAI GPT-4o-mini** API to parse structured information such as contact details, skills, experience, education, certifications, and a summary.

If the OpenAI API is unavailable or fails, the module falls back to returning raw text with an empty structure.

## Package Structure

```
cv_processor/
├── __init__.py              # Package entry point (exports CVProcessor, exceptions)
├── processor.py             # Main orchestrator (CVProcessor class)
├── exceptions.py            # Custom exceptions (ProcessingError, ParsingError)
├── extractors/
│   ├── __init__.py
│   ├── pdf_extractor.py     # PDF text extraction (pdfplumber)
│   ├── docx_extractor.py    # DOCX text extraction (python-docx)
│   └── txt_extractor.py     # TXT text extraction (chardet encoding detection)
└── parsers/
    ├── __init__.py
    └── openai_parser.py     # OpenAI GPT-4o-mini structured CV parsing
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the `backend/` directory:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Process a file
```python
from cv_processor import CVProcessor

result = CVProcessor.process_file("path/to/resume.pdf")
print(result)
```

### Process raw text
```python
from cv_processor import CVProcessor

result = CVProcessor.process_text("John Doe, Python developer at Google...")
print(result)
```

### Process a directory of CVs
```python
from cv_processor import CVProcessor

results = CVProcessor.process_directory("path/to/cv_folder/")
for filename, data in results.items():
    print(filename, data)
```

## Output Format

```json
{
    "raw_text": "Full extracted CV text...",
    "parsed_data": {
        "contact": {
            "name": "Santiago Cardenas",
            "email": "santiago@example.com",
            "phone": "+1234567890",
            "location": "Toronto, ON",
            "linkedin": "linkedin.com/in/santiago"
        },
        "skills": ["Python", "NLP", "FastAPI"],
        "experience": [
            {
                "job_title": "Software Engineer",
                "company": "TechCorp",
                "start_date": "2020",
                "end_date": "2023",
                "description": "Built ML pipelines and REST APIs"
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science",
                "institution": "University of Toronto",
                "year": "2020",
                "field": "Computer Science"
            }
        ],
        "certifications": ["AWS Cloud Practitioner"],
        "summary": "Experienced software engineer specializing in NLP..."
    },
    "parsing_method": "openai",
    "metadata": {
        "file_type": "pdf",
        "text_length": 2340,
        "skills_count": 3,
        "experience_count": 1
    }
}
```

## Supported File Types

| Format | Library Used |
|--------|-------------|
| `.pdf`  | pdfplumber  |
| `.docx` | python-docx |
| `.doc`  | python-docx |
| `.txt`  | chardet     |

## Fallback Mode

When the OpenAI API key is missing or the API call fails, the module returns a minimal structure with `_fallback: true` and empty fields. This ensures the application does not crash.

## Running Tests

From the `backend/` directory:
```bash
python -m pytest tests/test_openai_parser.py -v
```

All tests use mocked OpenAI API calls, so no real API key is needed for testing.
