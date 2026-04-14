# CVMatch: Resume & Job Description Matching System
**Cambrian College — Graduate Certificate in Artificial Intelligence Natural Language Processing — Final Project**

**Authors:** Santiago Cárdenas & Amel Sunil
**Date:** 2026-04-13

---

## 1. Purpose

### Problem Definition
In modern hiring processes, candidates often struggle to objectively assess how well their resume aligns with a given job description. Manually comparing skills, experience, and qualifications is time-consuming and subjective, leading to inefficient applications and increased frustration for both candidates and recruiters.

### Motivation
With the growth of online job applications, there is a pressing need for automated tools that can quickly evaluate CV–job compatibility using natural language processing. Such tools can help candidates tailor their resumes and make informed decisions about which positions to pursue.

### Objective
Develop a fully functional, end-to-end NLP system that accepts a candidate's CV (PDF, DOCX, or TXT) and a job description, then computes a semantic match score along with actionable feedback including matched skills, missing skills, and a concise evaluation summary.

---

## 2. Solution Approach

### Methodology
The system follows a modular pipeline architecture:
1. File ingestion and text extraction
2. NLP preprocessing and AI-driven structured parsing
3. Semantic embedding generation (per section)
4. Similarity scoring with sigmoid calibration and actionable feedback

### Data Pipeline

| Step | Component              | Description |
|------|-----------------------|-------------|
| 1    | File Extraction       | PDF → pdfplumber; DOCX → python-docx; TXT → chardet |
| 2    | AI Parsing (GPT-4o-mini) | Extract structured fields: contact, skills, experience, education, education level, summary |
| 3    | AI Normalization (GPT-4o-mini) | Dedupe + lowercase skills, expand abbreviations, produce comparison-ready section paragraphs |
| 4    | JD Preprocessing (GPT-4o-mini) | Extract required/preferred skills, experience/education requirements, key phrases, summary |
| 5    | Section Embeddings    | OpenAI text-embedding-3-small → 1536-dim vectors for skills / experience / education / overall |
| 6    | Similarity Scoring    | Jaccard + fuzzy skill matching, cosine similarity, education & experience boosts |
| 7    | GPT Semantic Reconciliation (optional) | GPT-4o-mini pairs unmatched CV skills ↔ JD skills by meaning when keyword methods miss synonyms |
| 8    | Sigmoid Calibration   | Raw weighted sum (0–1) → human-readable 0–100% match |
| 9    | Feedback Generation   | Matched/missing/extra skills, strengths, gaps, recommendation band |

### NLP Techniques Employed
- **OpenAI text-embedding-3-small** — 1536-dim semantic embeddings for deep contextual matching
- **GPT-4o-mini structured extraction** — reliable parsing of unstructured CV and JD text into structured fields using JSON-mode responses
- **Section-level embeddings** — separate vectors for skills, experience, education, and overall content enable fine-grained matching
- **Jaccard + fuzzy matching** — word-boundary substring checks and `SequenceMatcher.ratio() ≥ 0.8` for catching typos, plurals, and partial matches
- **GPT-driven semantic skill reconciliation** — an LLM pass for pairing unmatched skills that are synonymous or where one is a specialization of the other
- **Sigmoid calibration** — raw similarity scores (typically clustered in 0.3–0.8) are passed through a sigmoid centered at 0.30 to stretch them into an intuitive 0–100 range

---

## 3. Technical Implementation & Architecture

### Tech Stack

| Layer              | Technology |
|-------------------|------------|
| Frontend          | Next.js 16, TypeScript, Tailwind CSS, Clerk (auth) |
| Backend / API     | FastAPI (Python 3.11) |
| LLM Parsing & Reconciliation | GPT-4o-mini (OpenAI) |
| Embeddings        | OpenAI text-embedding-3-small |
| Similarity Maths  | NumPy, scikit-learn (cosine similarity) |
| File Processing   | pdfplumber, python-docx, chardet |
| Persistence       | SQLite (embedding vector cache) |
| Testing           | pytest (backend) |
| Containerization  | Docker + docker-compose (backend + frontend services) |

### Architecture Overview
The system is split into a FastAPI backend and a Next.js frontend.

**Backend HTTP endpoints:**
- `POST /api/v1/match` — upload CV + job description, returns full match report
- `POST /api/v1/cv/upload` — parse a CV in isolation
- `POST /api/v1/jd/preprocess` — preprocess a job description in isolation

**Internal module layout:**

```
backend/
├── api/              # FastAPI entrypoint + CORS + logging config
├── routes/           # HTTP endpoints (match, cv, job_description)
├── cv_processor/     # Extractors (PDF/DOCX/TXT) + GPT-4o-mini parser
├── nlp_preprocessing # Text cleaner + CV normalizer + JD preprocessor
├── embedding/        # OpenAI encoder, section embeddings, SQLite vector cache
├── services/         # Orchestration: matching, similarity engine, openai retry
├── middleware/       # Per-request logging
└── prompts.py        # Central registry of all OpenAI prompts
```

Each module is independently unit-tested with `pytest`, and all OpenAI calls are wrapped in an exponential-backoff retry for transient rate-limit errors.

---

## 4. Core Functionalities

### Algorithms & Model Selection Rationale
- **GPT-4o-mini for parsing & extraction:** chosen over rule-based regex parsers because CVs vary wildly in formatting. The LLM produces structured JSON (enforced via `response_format={"type": "json_object"}`) which dramatically reduces downstream parsing errors.
- **text-embedding-3-small for similarity:** OpenAI's 1536-dim embeddings capture deep contextual meaning and handle paraphrasing naturally. Section-level embeddings allow separate scoring of skills / experience / education rather than flattening everything into a single vector.
- **Jaccard + fuzzy + semantic reconciliation for skills:** a three-tier strategy. Exact set intersection first (cheapest), fuzzy matching next (catches typos and partial matches), and GPT reconciliation last (handles synonyms like "teamwork" ↔ "interpersonal skills"). Each tier runs only on what the previous tier couldn't match, minimizing cost.
- **Education and experience boosts:** raw cosine similarity alone can undervalue candidates with the right degree or job title but different phrasing. Explicit level-based boosts (PhD > Master's > Bachelor's, job-title substring matching) correct for this.
- **Sigmoid calibration:** raw similarities from the weighted sum typically lie in 0.3–0.8. A sigmoid centered at 0.30 with steepness 8 maps that into 0–100% so users see intuitive numbers (0.45 raw → 83%, not 45%).
- **SQLite embedding cache:** repeated analyses of the same CV against different JDs skip parsing and embedding entirely, significantly reducing API cost on iterative use.

### Scoring Weights
The final match percentage is a weighted blend of five signals:

| Signal                | Weight | What it captures |
|-----------------------|--------|------------------|
| Overall semantic      | 30%    | Full-CV ↔ full-JD cosine similarity |
| Skills keyword match  | 25%    | Jaccard + fuzzy skill coverage |
| Experience match      | 25%    | Experience-section cosine + job-title overlap boost |
| Skills semantic match | 10%    | Skills-section cosine similarity |
| Education match       | 10%    | Education-section cosine + level-based boost |

### Design Trade-offs
- **OpenAI API cost vs. accuracy:** every match makes up to 6 OpenAI calls (parse, normalize, JD extract, 2× embedding batches, optional semantic reconciliation). The SQLite cache skips the parse/normalize/embed calls on repeat matches of the same CV, cutting cost significantly after the first run.
- **Structured pipeline vs. end-to-end LLM:** rather than feeding the raw CV and JD to a single LLM and asking for a match score, we pipeline discrete stages. This is more auditable, easier to debug, and cheaper than repeated long-context LLM calls.
- **Fail-loud vs. graceful degradation:** during development, an earlier "fallback" scoring path (raw-text embedding + TF-IDF keyword similarity) was tested for when GPT parsing failed. Observed behavior was that it produced misleading low scores (~10%) for clearly matching CVs because literal word overlap between a CV and JD is low even when they describe the same role. The fallback was removed in favor of an explicit HTTP 503 response so users retry instead of receiving a misleading number.
- **Modularity vs. simplicity:** the backend is split into ~10 modules with clear responsibilities. This adds some boilerplate (service wrappers, explicit dependency injection) but makes unit testing and future refactors much easier.

---

## 5. Result Analysis

Performance was evaluated on a set of 20 sample CV–job description pairs with known ground-truth match labels (High / Medium / Low). Two variants were compared during development:

| Metric                         | TF-IDF baseline (keyword only) | OpenAI embeddings + Jaccard + boosts (current) |
|--------------------------------|--------------------------------|-------------------------------------------------|
| Precision (High / Medium / Low) | 0.65 / 0.68 / 0.71            | 0.85 / 0.87 / 0.82 |
| Recall (High / Medium / Low)    | 0.60 / 0.72 / 0.69            | 0.83 / 0.86 / 0.80 |
| F1-Score (High / Medium / Low)  | 0.62 / 0.70 / 0.70            | 0.84 / 0.86 / 0.81 |
| Avg. match-score accuracy       | 68.4%                          | 87.1% |
| Avg. response time              | 1.2 s                          | 2.1 s (first match) · 0.5 s (cached) |

### Interpretation
The current OpenAI-based architecture — section embeddings combined with Jaccard skill matching and education/experience boosts — consistently outperforms the TF-IDF baseline across all match categories. The largest gains appear in the **High** match category (+20pp precision), where deep semantic understanding matters most for distinguishing genuinely strong fits from merely keyword-overlapping ones. The SQLite cache makes repeat matches sub-second, which is critical for iterative use (comparing the same CV against multiple JDs).

A TF-IDF-only fallback was initially implemented for resilience when the OpenAI API was unavailable. During testing it became clear that TF-IDF on full CV/JD text produces near-random scores (a well-matching pair scored 9.6%) because candidates rarely copy the exact wording of a job posting. The fallback was removed in favor of returning HTTP 503 with a clear retry message — honesty over faux resilience.

### Key Findings
1. **Structured LLM parsing dramatically outperforms rule-based extraction** on skills and experience fields, especially for CVs with non-standard formatting.
2. **Section-level embeddings enable useful feedback.** Separating skills / experience / education vectors lets the system explain *why* a match is strong or weak, not just produce a number.
3. **Sigmoid calibration was essential.** Raw cosine similarities concentrate in 0.3–0.8; without calibration, users perceived the scores as uniformly low.
4. **A misleading score is worse than no score.** Removing the TF-IDF fallback and returning an explicit error when OpenAI is unavailable improved user trust at the cost of a small reliability window.
5. **Modular architecture paid off.** Removing an entire scoring branch (TF-IDF + fallback paths), consolidating prompts into a single file, and adding a live calculation display on the frontend all took hours rather than days because the boundaries between modules were clear.

---
