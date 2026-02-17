# CV Processor Module

A robust Python module for extracting text and structured information from various resume formats (PDF, DOCX, TXT).

## Features

- **Multi-format Support**: Extract text from PDF, DOCX, and TXT files
- **Structured Data Extraction**: Automatically parse contact info, skills, work experience, and education
- **Text Normalization**: Clean and standardize extracted text
- **Error Handling**: Graceful handling of corrupted or unsupported files
- **Skill Standardization**: Convert abbreviations and standardize skill names
- **Batch Processing**: Process multiple CV files from a directory
- **Contact Parsing**: Extract name, email, and phone using regex patterns
- **Date Standardization**: Handle various date formats

## Installation

### Requirements
All dependencies are listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `pdfplumber` - PDF text extraction
- `python-docx` - DOCX file parsing
- `chardet` - Encoding detection for TXT files
- `pytest` - Testing framework (optional, for running tests)

## File Structure

```
cv_processor/
├── __init__.py                 # Package initialization
├── cv_processor.py             # Main CVProcessor class
├── normalizer.py               # Text normalization utilities
├── test_cv_processor.py        # Comprehensive pytest test suite
├── extractors/
│   ├── __init__.py
│   ├── pdf_extractor.py       # PDF text extraction
│   ├── docx_extractor.py      # DOCX text extraction
│   └── txt_extractor.py       # TXT text extraction with encoding detection
└── parsers/
    ├── __init__.py
    ├── contact_parser.py      # Extract name, email, phone
    ├── skills_parser.py       # Extract and standardize skills
    └── experience_parser.py   # Extract work experience and education
```

## Usage

### Basic Usage

#### Process a Single File

```python
from nlp.cv_processor import CVProcessor

# Process a PDF file
result = CVProcessor.process_file("path/to/resume.pdf")

# Process a DOCX file
result = CVProcessor.process_file("path/to/resume.docx")

# Process a TXT file
result = CVProcessor.process_file("path/to/resume.txt")
```

#### Process Raw Text

```python
from nlp.cv_processor import CVProcessor

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
from nlp.cv_processor import CVProcessor

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
    "skills": ["Python", "JavaScript", "React", "FastAPI"],
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

## API Reference

### CVProcessor

Main class for processing CVs and extracting structured information.

#### Methods

**`process_file(file_path: str) -> Dict[str, Any]`**
- Process a single CV file (PDF, DOCX, or TXT)
- **Parameters:**
  - `file_path` (str): Path to the CV file
- **Returns:** Dictionary with extracted information
- **Raises:**
  - `FileNotFoundError`: If file doesn't exist
  - `ValueError`: If file format is unsupported or text extraction fails

**`process_text(text: str) -> Dict[str, Any]`**
- Process raw CV text
- **Parameters:**
  - `text` (str): Raw CV text
- **Returns:** Dictionary with extracted information
- **Raises:**
  - `ValueError`: If text is empty or None

**`process_directory(directory_path: str) -> Dict[str, Dict[str, Any]]`**
- Process all CV files in a directory
- **Parameters:**
  - `directory_path` (str): Path to directory containing CV files
- **Returns:** Dictionary mapping filenames to processed CV data
- **Raises:**
  - `ValueError`: If directory doesn't exist

### Text Extractors

#### PDFExtractor

```python
from nlp.cv_processor.extractors import PDFExtractor

text = PDFExtractor.extract("resume.pdf")
# Returns: str or None if extraction fails
```

**Features:**
- Multi-page document support
- Password-protected file detection
- Error handling for corrupted PDFs

#### DOCXExtractor

```python
from nlp.cv_processor.extractors import DOCXExtractor

text = DOCXExtractor.extract("resume.docx")
# Returns: str or None if extraction fails
```

**Features:**
- Paragraph extraction
- Table content extraction
- Structure preservation

#### TXTExtractor

```python
from nlp.cv_processor.extractors import TXTExtractor

text = TXTExtractor.extract("resume.txt")
# Returns: str or None if extraction fails
```

**Features:**
- Automatic encoding detection
- Handles various text encodings (UTF-8, ASCII, etc.)
- Error recovery

### Information Parsers

#### ContactParser

```python
from nlp.cv_processor.parsers import ContactParser

contact = ContactParser.extract(cv_text)
# Returns: {"name": str, "email": str, "phone": str}
```

**Supported Formats:**
- **Emails:** john@example.com, john.doe@company.co.uk
- **Phones:** 
  - +1-555-123-4567
  - (555) 123-4567
  - 555.123.4567
  - +1 555 123 4567

#### SkillsParser

```python
from nlp.cv_processor.parsers import SkillsParser

skills = SkillsParser.extract(cv_text)
# Returns: ["Python", "JavaScript", "React", ...]
```

**Features:**
- 34+ skill mappings
- Abbreviation support (JS→JavaScript, ML→Machine Learning, etc.)
- Duplicate removal
- Skill standardization

**Supported Skills Include:**
- Languages: Python, Java, JavaScript, TypeScript, C++, C#, SQL
- Frameworks: React, Angular, Vue, Django, FastAPI, Flask, Spring Boot
- Databases: PostgreSQL, MySQL, MongoDB
- Cloud: AWS, Google Cloud, Azure
- ML/AI: Machine Learning, Deep Learning, TensorFlow, PyTorch, Scikit-learn
- And 10+ more...

#### ExperienceParser

```python
from nlp.cv_processor.parsers import ExperienceParser

experience = ExperienceParser.extract_experience(cv_text)
education = ExperienceParser.extract_education(cv_text)
```

**Features:**
- Work experience extraction with dates
- Job title and company parsing
- Education degree and institution extraction
- GPA extraction
- Date format standardization

### Normalizer

Text normalization and standardization utilities.

```python
from nlp.cv_processor.normalizer import Normalizer

# Basic text normalization
normalized = Normalizer.normalize_text(text)

# Clean text (remove special characters)
cleaned = Normalizer.clean_text(text, preserve_structure=True)

# Expand abbreviations
expanded = Normalizer.expand_abbreviations(text)

# Standardize skills
standardized_skills = Normalizer.standardize_skills(skills_list)

# Handle various date formats
date = Normalizer.handle_date_formats("January 2020")
```

## Testing

Run the comprehensive test suite:

```bash
# From backend directory
python -m pytest nlp/cv_processor/test_cv_processor.py -v

# Or using Python module execution
python -m nlp.cv_processor.test_cv_processor
```

**Test Coverage:**
- 60+ test cases
- PDF, DOCX, TXT extraction tests
- Contact, skills, experience parsing tests
- Text normalization tests
- Error handling and edge cases
- Full workflow integration tests

## Examples

### Example 1: Extract Information from a PDF Resume

```python
from nlp.cv_processor import CVProcessor
import json

result = CVProcessor.process_file("john_doe_resume.pdf")

print("Contact Information:")
print(f"  Name: {result['contact']['name']}")
print(f"  Email: {result['contact']['email']}")
print(f"  Phone: {result['contact']['phone']}")

print("\nSkills:")
for skill in result['skills']:
    print(f"  - {skill}")

print("\nWork Experience:")
for exp in result['experience']:
    print(f"  - {exp['title']} at {exp['company']}")
    print(f"    {exp['start_date']} to {exp['end_date']}")

print("\nEducation:")
for edu in result['education']:
    print(f"  - {edu['degree']}")
    print(f"    {edu['institution']} ({edu['graduation_date']})")
```

### Example 2: Batch Processing CV Directory

```python
from nlp.cv_processor import CVProcessor

# Process all CVs in a folder
results = CVProcessor.process_directory("resumes/")

# Summary statistics
success_count = sum(1 for r in results.values() if "error" not in r)
print(f"Successfully processed: {success_count}/{len(results)} files")

# Collect all unique skills
all_skills = set()
for data in results.values():
    if "error" not in data:
        all_skills.update(data['skills'])

print(f"\nAll skills found: {sorted(all_skills)}")
```

### Example 3: Process Text with Error Handling

```python
from nlp.cv_processor import CVProcessor

cv_text = """
Alice Johnson
alice.johnson@tech.com

SKILLS: Python, Machine Learning, FastAPI, Docker

WORK EXPERIENCE
ML Engineer at DataCo
2021 - Present
"""

try:
    result = CVProcessor.process_text(cv_text)
    print(f"Extracted {len(result['skills'])} skills")
    print(f"Contact: {result['contact']['name']}")
except ValueError as e:
    print(f"Error: {e}")
```

## Skill Abbreviations Supported

| Abbreviation | Expansion |
|---|---|
| js | JavaScript |
| ts | TypeScript |
| ml | Machine Learning |
| ai | Artificial Intelligence |
| dl | Deep Learning |
| nlp | NLP |
| cpp | C++ |
| c# | C# |
| sql | SQL |

*And 25+ more... See `SkillsParser.SKILLS_MAPPING` for complete list*

## Error Handling

The module gracefully handles errors:

```python
from nlp.cv_processor import CVProcessor

# Handle file errors
try:
    result = CVProcessor.process_file("nonexistent.pdf")
except FileNotFoundError:
    print("File not found")

# Handle format errors
try:
    result = CVProcessor.process_file("document.xlsx")
except ValueError as e:
    print(f"Unsupported format: {e}")

# Handle empty text
try:
    result = CVProcessor.process_text("")
except ValueError:
    print("Empty text provided")

# Batch processing with error tracking
results = CVProcessor.process_directory("cvs/")
for filename, data in results.items():
    if "error" in data:
        print(f"Failed to process {filename}: {data['error']}")
```

## Performance

- **PDF Files**: Fast extraction, handles multi-page documents
- **DOCX Files**: Efficient paragraph and table parsing
- **TXT Files**: Automatic encoding detection
- **Batch Processing**: Process 100+ CVs in seconds

## Limitations

- **Password-protected PDFs**: Cannot extract from encrypted PDFs
- **Scanned PDFs**: OCR not supported (requires image-based PDFs)
- **Complex Layouts**: Best with standard CV formats
- **Language Support**: Optimized for English resumes

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Multi-language support
- [ ] Advanced entity recognition with spaCy NER
- [ ] Portfolio/GitHub link extraction
- [ ] Certifications parsing
- [ ] Languages spoken extraction

## Contributing

To add new features:

1. Add new extractors in `extractors/`
2. Add new parsers in `parsers/`
3. Add comprehensive tests in `test_cv_processor.py`
4. Update this README

## License

Part of the CV Matching Project - Cambrian College NLP Semester 2

## Support

For issues or questions, refer to the test file for usage examples:
```bash
nlp/cv_processor/test_cv_processor.py
```

---


