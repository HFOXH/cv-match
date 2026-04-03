# CVMatch: Chat-Based NLP System for Resume and Job Description Matching

**Project Authors:** Santiago Cárdenas & Amel Sunil  
**First Version:** 2025-02-27  
**Last Updated:** 2026-04-03  
**Tech Stack:** Python, FastAPI, Next.js, TypeScript, OpenAI Embeddings, TF-IDF, Sentence-BERT, spaCy, NLTK  

---

## Overview

CVMatch is an interactive system designed to help candidates quickly evaluate how well they fit a specific job opportunity. Through a simple interface, users upload their CV along with a job description, and the system analyzes both to generate a compatibility score.

Using semantic analysis, CVMatch calculates a match percentage that reflects how closely the candidate’s skills, experience, and profile align with the job requirements. In addition to the score, the system provides a concise summary of the evaluation, highlights strengths, and identifies missing or weak areas that could be improved.

The project is composed of two main modules:

Backend: Handles CV processing, semantic analysis, and similarity computation.
Frontend: Provides a user-friendly interface where users submit their CV and job description, and visualize results through an interactive chat-based experience. 

---

## Project Architecture

```
CVMatch/
├─ backend/
│  ├─ api/                      # FastAPI application
│  │   └─ main.py
│  ├─ cv_processor/             # CV processing and extraction
│  │   ├─ extractors/           # PDF, DOCX, TXT extraction
│  │   │   ├─ pdf_extractor.py
│  │   │   ├─ docx_extractor.py
│  │   │   └─ txt_extractor.py
│  │   ├─ parsers/              # AI-powered CV parsing
│  │   │   └─ openai_parser.py
│  │   ├─ processor.py          # CVProcessor class
│  │   └─ exceptions.py        # ProcessingError, ParsingError
│  ├─ embedding/                # Text embedding encoders
│  │   ├─ openai_encoder.py    # OpenAI text-embedding-3-small
│  │   ├─ tfidf_encoder.py     # TF-IDF vectorizer
│  │   ├─ hybrid_encoder.py    # Combined embedding approach
│  │   ├─ vector_store.py      # Vector similarity storage
│  │   └─ section_embeddings.py # Section-level embeddings
│  ├─ nlp_preprocessing/        # Text preprocessing
│  │   ├─ cleaner.py           # Text cleaning utilities
│  │   ├─ cv_normalizer.py     # CV normalization
│  │   └─ job_preprocessor.py  # Job description preprocessing
│  ├─ services/                 # Business logic services
│  │   ├─ matching_service.py   # Match calculation logic
│  │   ├─ similarity_engine.py  # Similarity computation
│  │   ├─ cv_service.py         # CV processing service
│  │   ├─ openai_retry.py       # Retry logic for API calls
│  │   ├─ normalization_service.py
│  │   └─ job_description_service.py
│  ├─ routes/                   # API endpoints
│  │   ├─ cv.py                # CV upload endpoints
│  │   ├─ match.py             # Match endpoints
│  │   └─ job_description.py   # Job description endpoints
│  ├─ middleware/               # Request/response middleware
│  │   └─ request_logger.py    # Request logging
│  ├─ tests/                    # Unit and integration tests
│  └─ requirements.txt          # Python dependencies
├─ frontend/                    # Next.js web application
│  ├─ app/
│  │   ├─ layout.tsx           # Global app layout
│  │   ├─ page.tsx             # Main landing page
│  │   ├─ providers.tsx        # React providers
│  │   ├─ proxy.ts             # API proxy
│  │   ├─ analyzer/            # Analyzer page
│  │   │   └─ page.tsx
│  │   ├─ terms/               # Terms of service
│  │   │   └─ page.tsx
│  │   ├─ privacy/             # Privacy policy
│  │   │   └─ page.tsx
│  │   └─ support/             # Support page
│  │       └─ page.tsx
│  ├─ components/
│  │   ├─ MatchCircle.tsx      # Match percentage visual
│  │   ├─ Navbar.tsx           # Navigation bar
│  │   ├─ Footer.tsx           # Footer component
│  │   ├─ ThemeToggle.tsx     # Dark/light theme toggle
│  │   ├─ Paywall.tsx          # Paywall component
│  │   └─ FeatureComparison.tsx # Feature comparison table
│  ├─ public/                  # Static assets
│  ├─ globals.css             # Global styles
│  └─ package.json
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
│   ├── __init__.py
│   ├── pdf_extractor.py
│   ├── docx_extractor.py
│   └── txt_extractor.py
└── parsers/
    ├── __init__.py
    └── openai_parser.py
```

### Embedding Module

The `embedding` module provides text vectorization for semantic similarity:

- `openai_encoder.py` - OpenAI text-embedding-3-small integration
- `tfidf_encoder.py` - TF-IDF vectorizer for keyword-based matching
- `hybrid_encoder.py` - Combined approach using both methods
- `vector_store.py` - Vector storage and similarity search
- `section_embeddings.py` - Section-level embedding for detailed matching

### NLP Preprocessing Module

The `nlp_preprocessing` module handles text cleaning and normalization:

- `cleaner.py` - Text cleaning utilities (removing special chars, normalizing whitespace)
- `cv_normalizer.py` - CV text normalization
- `job_preprocessor.py` - Job description preprocessing

### Services Module

The `services` module contains business logic:

- `matching_service.py` - Match calculation logic
- `similarity_engine.py` - Similarity computation engine
- `cv_service.py` - CV processing service
- `openai_retry.py` - Retry logic with exponential backoff
- `normalization_service.py` - Data normalization
- `job_description_service.py` - Job description handling

### Routes Module

API endpoints:

- `cv.py` - CV upload and processing endpoints
- `match.py` - Match calculation endpoints
- `job_description.py` - Job description endpoints

### Middleware

- `request_logger.py` - Request/response logging middleware

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

- Uploading CVs (`/api/cv`)
- Submitting job descriptions (`/api/job_description`)
- Calculating match (`/api/match`)

**Structure:**

```
backend/api/
├── main.py           # FastAPI application
└── routes/
    ├── cv.py                # CV endpoints
    ├── match.py             # Match endpoints
    └── job_description.py   # Job description endpoints
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

**Running Backend**
```bash
uvicorn api.main:app --reload
```

---

## Frontend Documentation

- **Framework:** Next.js with TypeScript and Tailwind CSS
- **Features:**
  - Upload CVs and job descriptions
  - Interactive chat with instant feedback
  - Match percentage visualization using `MatchCircle.tsx`
  - Theme toggle (dark/light mode)
  - Terms, privacy policy, and support pages

- **Pages:**

| Page | File | Description |
|------|------|-------------|
| Home | `app/page.tsx` | Landing page |
| Analyzer | `app/analyzer/page.tsx` | CV analysis page |
| Terms | `app/terms/page.tsx` | Terms of service |
| Privacy | `app/privacy/page.tsx` | Privacy policy |
| Support | `app/support/page.tsx` | Support page |

- **Components:**

| Component | File | Description |
|-----------|------|-------------|
| MatchCircle | `components/MatchCircle.tsx` | Match percentage visualization |
| Navbar | `components/Navbar.tsx` | Navigation bar |
| Footer | `components/Footer.tsx` | Footer component |
| ThemeToggle | `components/ThemeToggle.tsx` | Dark/light mode toggle |
| Paywall | `components/Paywall.tsx` | Paywall component |
| FeatureComparison | `components/FeatureComparison.tsx` | Feature comparison table |

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

Backend tests (pytest, OpenAI calls are mocked):

```bash
cd backend
pytest -v
```

Test files include:
- `tests/test_similarity_engine.py` - Similarity engine tests
- `tests/test_openai_encoder.py` - OpenAI encoder tests
- `tests/test_tfidf_encoder.py` - TF-IDF encoder tests
- `tests/test_hybrid_encoder.py` - Hybrid encoder tests
- `tests/test_cv_normalizer.py` - CV normalizer tests
- `tests/test_job_preprocessor.py` - Job preprocessor tests
- `tests/test_cleaner.py` - Text cleaner tests
- `tests/test_vector_store.py` - Vector store tests
- `tests/test_section_embeddings.py` - Section embeddings tests
- `tests/test_openai_parser.py` - OpenAI parser tests

Frontend: use `npm run dev` and test interaction on localhost.

---

## Future Improvements

- Multilingual support for CVs and job descriptions.
- Advanced semantic matching using more sophisticated embeddings (OpenAI embeddings / LLMs).
- Dashboard for match statistics for frequent users.
- Integration with LinkedIn API for automatic CV extraction.
- Resume optimization suggestions based on match analysis.

---
