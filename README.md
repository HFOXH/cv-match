# CVMatch: Chat-Based NLP System for Resume and Job Description Matching

**Project Authors:** Santiago Cárdenas & Amel Sunil  
**First Version:** 2025-02-27  
**Tech Stack:** Python, FastAPI, Streamlit / Next.js, Sentence-BERT, spaCy, NLTK  

---

## Overview

CVMatch is a chat-based system that helps candidates quickly and semantically evaluate their compatibility with job postings. The system analyzes an uploaded CV and a job description, calculating a **match percentage** that reflects how well the candidate's skills and experience align with the job requirements.

The project consists of **two main modules**:  

1. **Backend:** CV processing, semantic analysis, and similarity computation.  
2. **Frontend:** Web chat interface for user interaction and results visualization.  

---

## Project Architecture

```
CVMatch/
├─ backend/
│   ├─ cv_processor/          # CV processing and extraction
│   ├─ api/                   # FastAPI endpoints
│   ├─ requirements.txt       # Libraries
│   └─ .env                   # API keys and configuration
├─ frontend/                  # Web application (Next.js + TypeScript)
│   ├─ app/
│   │   ├─ layout.tsx         # Global app layout
│   │   └─ page.tsx           # Main chat page
│   ├─ components/
│   │   └─ MatchCircle.tsx    # Match percentage visual component
│   ├─ public/                # Icons and assets
│   └─ globals.css
└─ README.md
```

---

## Backend Documentation

### CV Processor Module

The `cv_processor` module handles:

- Extracting text from CVs (PDF, DOCX, TXT).  
- Parsing structured data using GPT-4o-mini (contact info, skills, experience, education, certifications, summary).  
- Generating semantic vectors for similarity computation with job descriptions.  

#### Package Structure

```
cv_processor/
├── __init__.py
├── processor.py             # CVProcessor class
├── exceptions.py            # ProcessingError, ParsingError
├── extractors/
│   ├── pdf_extractor.py
│   ├── docx_extractor.py
│   └── txt_extractor.py
└── parsers/
    └── openai_parser.py
```

#### Usage

```python
from cv_processor import CVProcessor

# Process a single file
result = CVProcessor.process_file("path/to/resume.pdf")

# Process raw text
result = CVProcessor.process_text("John Doe, Python developer at Google...")

# Process a directory of CVs
results = CVProcessor.process_directory("path/to/cv_folder/")
```

#### Output Format

```json
{
  "raw_text": "Full CV text...",
  "parsed_data": {
    "contact": {...},
    "skills": ["Python", "NLP"],
    "experience": [...],
    "education": [...],
    "certifications": [...],
    "summary": "..."
  },
  "parsing_method": "openai",
  "metadata": {...}
}
```

#### Supported File Types

| Format | Library Used |
|--------|-------------|
| `.pdf`  | pdfplumber  |
| `.docx` | python-docx |
| `.doc`  | python-docx |
| `.txt`  | chardet     |

#### Fallback Mode

If the OpenAI API fails, raw text is returned with `_fallback: true`.

---

### FastAPI Backend

The backend exposes endpoints for:  

- Uploading CVs (`/upload_cv`)  
- Submitting job descriptions (`/match_job`)  
- Receiving match percentage and detailed match information  

**Structure:**

```
backend/api/
├── main.py          # FastAPI app
├── endpoints/
│   ├── upload.py
│   └── match.py
```

**Example request:**

```bash
POST /match_job
{
    "cv_file": "resume.pdf",
    "job_description": "Looking for a Python engineer with NLP experience..."
}
```

**Response:**

```json
{
  "match_percentage": 87,
  "skills_matched": ["Python", "NLP"],
  "missing_skills": ["AWS"],
  "summary": "Your profile fits this position very well."
}
```

---

## Frontend Documentation

- **Framework:** Next.js with TypeScript and Tailwind CSS  
- **Features:**  
  - Upload CVs and job descriptions  
  - Interactive chat with instant feedback  
  - Match percentage visualization using `MatchCircle.tsx`  

- **Main structure:**

```
frontend/
├─ app/                # Pages and layouts
├─ components/         # Reusable React components
├─ public/             # Assets (SVG, ICO)
├─ globals.css         # Global styles
```

**Start frontend (development):**

```bash
cd frontend
npm install
npm run dev
```

---

## Setup

1. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Create a `.env` file with OpenAI API Key:

```
OPENAI_API_KEY=your-api-key-here
```

3. Install frontend dependencies:

```bash
cd frontend
npm install
npm run dev
```

---

## Testing

- Backend tests (pytest, OpenAI calls are mocked):

```bash
cd backend
pytest -v
```

- Frontend: use `npm run dev` and test interaction on localhost.

---

## Future Improvements

- Multilingual support for CVs and job descriptions.  
- Advanced semantic matching using more sophisticated embeddings (OpenAI embeddings / LLMs).  
- Dashboard for match statistics for frequent users.  
- Integration with LinkedIn API for automatic CV extraction.

---
