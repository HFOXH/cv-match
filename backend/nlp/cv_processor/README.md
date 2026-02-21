# CV Processor Module

A robust Python module for extracting text and structured information from various resume formats (PDF, DOCX, TXT). Uses **spaCy PhraseMatcher** for NLP-powered skill extraction.

## Features

- **Multi-format Support**: Extract text from PDF, DOCX, and TXT files
- **NLP-Powered Skill Extraction**: spaCy PhraseMatcher with 227+ skill patterns across 12 categories
- **Two-Stage Skill Detection**: Document-wide PhraseMatcher scan + section-based extraction
- **Structured Data Extraction**: Automatically parse contact info, skills, work experience, and education
- **Text Normalization**: Clean and standardize extracted text
- **Error Handling**: Graceful handling of corrupted or unsupported files
- **International Phone Support**: Handles US, international, and various phone formats
- **Batch Processing**: Process multiple CV files from a directory
- **Date Standardization**: Handle various date formats

## Installation

### Requirements
All dependencies are listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `spacy` - NLP tokenization and PhraseMatcher
- `pdfplumber` - PDF text extraction
- `python-docx` - DOCX file parsing
- `chardet` - Encoding detection for TXT files
- `pytest` - Testing framework (optional, for running tests)

### spaCy Model Setup

The skills parser requires the `en_core_web_sm` model:

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

> **Note:** If spaCy or the model is not installed, the parser automatically falls back to regex-based matching. spaCy is recommended for better accuracy.

## File Structure

```
cv_processor/
├── __init__.py                 # Package initialization
├── cv_processor.py             # Main CVProcessor class
├── normalizer.py               # Text normalization utilities
├── test_cv_processor.py        # Comprehensive pytest test suite (42 tests)
├── extractors/
│   ├── __init__.py
│   ├── pdf_extractor.py       # PDF text extraction
│   ├── docx_extractor.py      # DOCX text extraction
│   └── txt_extractor.py       # TXT text extraction with encoding detection
└── parsers/
    ├── __init__.py
    ├── contact_parser.py      # Extract name, email, phone
    ├── skills_parser.py       # spaCy PhraseMatcher skill extraction
    ├── skills_database.py     # 227+ skills organized by category
    └── experience_parser.py   # Extract work experience and education
```

**Utility scripts** (in `backend/nlp/`):
- `run_cv_processor.py` - CLI tool to process any PDF and output JSON
- `test_my_cv.py` - Test full pipeline on a resume
- `test_spacy.py` - Verify spaCy is active and working

## How Skill Extraction Works

The `SkillsParser` uses a **two-stage pipeline**:

### Stage 1: Document-Wide PhraseMatcher

spaCy tokenizes the entire CV text into linguistic tokens, then the PhraseMatcher scans all tokens in a **single pass** against 227+ known skill patterns.

```
Text: "Experienced in Python, machine learning, and React Native"
Tokens: [Experienced, in, Python, ,, machine, learning, ,, and, React, Native]
Matches: Python, Machine Learning, React Native, React
```

**Why spaCy over regex?**
- Keeps `C++`, `Node.js`, `.NET` as single tokens (regex would break on `.` and `+`)
- Single pass over the document instead of 227+ separate regex searches
- Handles multi-word skills like `"machine learning"` and `"spring boot"` naturally

### Stage 2: Section-Based Extraction

Finds the explicit "Skills" section in the resume and extracts items by splitting on commas, bullets, and newlines. This catches skills **not in the database** (e.g., domain-specific skills like "System Administration").

### Graceful Fallback

If spaCy is not installed, the parser falls back to regex-based matching automatically. Run `test_spacy.py` to check which mode is active.

## Usage

### CLI Tool

Process any PDF from the command line:

```bash
cd backend/nlp
python run_cv_processor.py "path/to/resume.pdf"
```

Outputs the full JSON result to stdout.

### Python API

#### Process a Single File

```python
from cv_processor.cv_processor import CVProcessor

# Process a PDF file
result = CVProcessor.process_file("path/to/resume.pdf")

# Process a DOCX file
result = CVProcessor.process_file("path/to/resume.docx")

# Process a TXT file
result = CVProcessor.process_file("path/to/resume.txt")
```

#### Process Raw Text

```python
from cv_processor.cv_processor import CVProcessor

cv_text = """
John Doe
john.doe@example.com
+1 (555) 123-4567

SKILLS
Python, JavaScript, React, FastAPI, Machine Learning

EXPERIENCE
Senior Developer at Tech Corp
January 2020 - Present
- Led NLP projects
- Managed ML pipelines

EDUCATION
Bachelor of Science in Computer Science
University of Technology
2018
"""

result = CVProcessor.process_text(cv_text)
```

#### Process Multiple Files

```python
from cv_processor.cv_processor import CVProcessor

# Process all CV files in a directory
results = CVProcessor.process_directory("/path/to/cv_folder")

for filename, data in results.items():
    if "error" not in data:
        print(f"\n{filename}:")
        print(f"  Name: {data['contact']['name']}")
        print(f"  Email: {data['contact']['email']}")
        print(f"  Skills: {', '.join(data['skills'])}")
    else:
        print(f"{filename}: Error - {data['error']}")
```

## Output Format

All processing methods return a dictionary with the following structure:

```python
{
    "raw_text": "Full CV text...",
    "normalized_text": "Normalized CV text...",
    "contact": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567"
    },
    "skills": ["Python", "JavaScript", "React", "FastAPI", "Machine Learning"],
    "experience": [
        {
            "title": "Senior Developer",
            "company": "Tech Corp",
            "start_date": "January 2020",
            "end_date": "Present",
            "description": ["Led NLP projects", "Managed ML pipelines"]
        }
    ],
    "education": [
        {
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University of Technology",
            "graduation_date": "2018",
            "gpa": None
        }
    ]
}
```

## Skills Database

The skills database (`parsers/skills_database.py`) contains **227+ skill patterns** organized into 12 categories:

| Category | Examples | Count |
|---|---|---|
| Programming Languages | Python, JavaScript, C++, Go, Rust | 34 |
| Web Frameworks | React, Angular, Django, FastAPI, Next.js | 45 |
| Databases | PostgreSQL, MongoDB, Redis, DynamoDB | 20 |
| Cloud & DevOps | AWS, Docker, Kubernetes, CI/CD | 25 |
| Data Science & ML | TensorFlow, PyTorch, Pandas, NLP, LLM | 45 |
| Tools & Version Control | Git, GitHub, Jira, Figma, Postman | 17 |
| APIs & Protocols | REST API, GraphQL, gRPC, WebSocket, JWT | 12 |
| Web Fundamentals | HTML, CSS, SASS, SEO | 7 |
| Testing | Pytest, Jest, Selenium, Cypress | 6 |
| Mobile | React Native, Flutter, Android, iOS | 6 |
| Security | Ethical Hacking, OWASP, Kali Linux, Nmap | 11 |
| Methodologies | Agile, Scrum, DevOps, Microservices, OOP | 9 |

Each skill maps lowercase variants to a canonical display name (e.g., `'js' -> 'JavaScript'`, `'k8s' -> 'Kubernetes'`).

To add a new skill, find the appropriate category in `skills_database.py` and add the entry.

## API Reference

### CVProcessor

Main class for processing CVs and extracting structured information.

#### Methods

**`process_file(file_path: str) -> Dict[str, Any]`**
- Process a single CV file (PDF, DOCX, or TXT)
- **Raises:** `FileNotFoundError`, `ValueError`

**`process_text(text: str) -> Dict[str, Any]`**
- Process raw CV text
- **Raises:** `ValueError` if text is empty or None

**`process_directory(directory_path: str) -> Dict[str, Dict[str, Any]]`**
- Process all CV files in a directory
- **Raises:** `ValueError` if directory doesn't exist

### Text Extractors

| Extractor | Format | Features |
|---|---|---|
| `PDFExtractor` | PDF | Multi-page, password detection, error recovery |
| `DOCXExtractor` | DOCX | Paragraphs, tables, structure preservation |
| `TXTExtractor` | TXT | Auto encoding detection (UTF-8, ASCII, etc.) |

### Information Parsers

#### ContactParser
```python
from cv_processor.parsers import ContactParser
contact = ContactParser.extract(cv_text)
# Returns: {"name": str, "email": str, "phone": str}
```

**Supported Phone Formats:**
- US: `(555) 123-4567`, `555-123-4567`, `555.123.4567`
- International: `(+57) 3132904901`, `+44 20 7946 0958`
- General: `+1-555-123-4567`, `+1 555 123 4567`

#### SkillsParser
```python
from cv_processor.parsers import SkillsParser
skills = SkillsParser.extract(cv_text)
# Returns: ["Python", "JavaScript", "React", ...]
```

**Features:**
- 227+ skill patterns with spaCy PhraseMatcher
- Lazy-loaded singleton (model loads once on first call)
- Regex fallback if spaCy is unavailable
- Short/ambiguous token handling (`C`, `R` only matched in skills sections)
- Section-aware extraction for skills not in the database

#### ExperienceParser
```python
from cv_processor.parsers import ExperienceParser
experience = ExperienceParser.extract_experience(cv_text)
education = ExperienceParser.extract_education(cv_text)
```

**Features:**
- Section heading detection (line-start matching to avoid false positives)
- Date extraction with `Present`/`Current`/`Now` support
- Company name extraction from date lines (e.g., "Oct 2023 - Present Symplifica")
- Education degree, institution, GPA, and year range parsing

### Normalizer

```python
from cv_processor.normalizer import Normalizer

normalized = Normalizer.normalize_text(text)
cleaned = Normalizer.clean_text(text, preserve_structure=True)
expanded = Normalizer.expand_abbreviations(text)
standardized_skills = Normalizer.standardize_skills(skills_list)
date = Normalizer.handle_date_formats("January 2020")
```

## Testing

### Run Full Test Suite

```bash
cd backend/nlp
python -m pytest cv_processor/test_cv_processor.py -v
```

**Test Coverage (42 tests):**
- PDF, DOCX, TXT extraction tests
- Contact, skills, experience parsing tests
- Text normalization tests
- Error handling and edge cases
- Full workflow integration test

### Verify spaCy is Active

```bash
cd backend/nlp
python test_spacy.py
```

### Test with a Resume

```bash
cd backend/nlp
python test_my_cv.py
# or
python run_cv_processor.py "path/to/resume.pdf"
```

## Performance

- **Skill Extraction**: Single-pass PhraseMatcher over 227+ patterns (faster than 227 regex searches)
- **Lazy Loading**: spaCy model loads once on first call, not at import time
- **Tokenizer Only**: NER, parser, and lemmatizer disabled for ~10x faster processing
- **PDF Files**: Fast extraction, handles multi-page documents
- **Batch Processing**: Process 100+ CVs efficiently

## Limitations

- **Password-protected PDFs**: Cannot extract from encrypted PDFs
- **Scanned PDFs**: OCR not supported (requires image-based PDFs)
- **Complex Layouts**: Best with standard CV formats
- **Language Support**: Optimized for English resumes
- **Skills Database**: Domain-specific skills outside the database are only caught from explicit skills sections

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Multi-language support
- [ ] Portfolio/GitHub link extraction
- [ ] Certifications parsing
- [ ] Languages spoken extraction
- [ ] Dynamic skills database updates

## Contributing

To add new features:

1. Add new extractors in `extractors/`
2. Add new parsers in `parsers/`
3. Add new skills to `parsers/skills_database.py`
4. Add comprehensive tests in `test_cv_processor.py`
5. Update this README

## License

Part of the CV Matching Project - Cambrian College NLP Semester 2

---

<<<<<<< HEAD

=======
**Last Updated:** February 21, 2026
**Version:** 2.0
**Status:** Production Ready
>>>>>>> 715f882 (Upgrade skill extraction to spaCy PhraseMatcher and fix parsers)
