# API reference

Every backend endpoint, request shape, response shape, and error code.

**Base URL** (local): `http://localhost:8000`
**Interactive docs**: `http://localhost:8000/docs` (FastAPI auto-generated Swagger UI)

All endpoints accept JSON except file uploads, which use `multipart/form-data`. Responses are always JSON.

---

## `POST /api/v1/match`

The main endpoint. Uploads a CV, takes a job description, and returns a full match report.

### Request

`multipart/form-data`:

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | File | yes | PDF, DOCX, or TXT. Max 5 MB. |
| `job_description` | string | yes | Full JD text. |

**Example (curl):**

```bash
curl -X POST http://localhost:8000/api/v1/match \
  -F "file=@resume.pdf" \
  -F "job_description=We are hiring a senior Python engineer with NLP experience..."
```

### Success response — 200 OK

```json
{
  "cv_id": "e3b0c44298fc1c149afbf4c8996fb924",
  "match_score": 87.3,
  "match_percentage": 87.3,
  "match_rating": "Good Match",
  "recommendation": "Good candidate — apply with confidence",
  "confidence": "high",
  "overall_similarity": 67.0,
  "section_similarities": {
    "skills_match": 83.0,
    "skills_semantic": 83.0,
    "experience": 54.0,
    "education": 80.0
  },
  "raw_scores": {
    "skills_jaccard":   0.83,
    "skills_semantic":  0.62,
    "sbert_overall":    0.67,
    "experience_match": 0.54,
    "education_match":  0.80
  },
  "skill_details": {
    "score": 0.83,
    "matched_skills": ["python", "nlp", "fastapi"],
    "missing_skills": ["kubernetes"],
    "extra_skills": ["react", "typescript"],
    "matched_count": 3,
    "job_skills_count": 4,
    "cv_skills_count": 5
  },
  "breakdown": {
    "overall_semantic": { "score": 67.0, "weight": "30%" },
    "skills":           { "score": 83.0, "weight": "25%", "matched": [...], "missing": [...], "matched_count": "3/4" },
    "experience":       { "score": 54.0, "weight": "25%" },
    "education":        { "score": 80.0, "weight": "10%" }
  },
  "strengths": [
    "Strong match on: python, nlp, fastapi",
    "Experience aligns well with the role"
  ],
  "gaps": [
    "Missing skills: kubernetes"
  ],
  "cv_summary": "Senior Python engineer with 5 years of NLP experience...",
  "job_summary": "Hiring a senior Python engineer to own the NLP pipeline...",
  "normalized_skills": ["python", "nlp", "fastapi", "react", "typescript"],
  "required_skills": ["python", "nlp", "fastapi", "kubernetes"],
  "preferred_skills": ["docker"],
  "experience_years": "5+ years",
  "education_level": "Bachelor's",
  "key_phrases": ["python engineer", "nlp pipeline", "production systems"],
  "timing": {
    "cv_processing_ms": 1200,
    "cv_normalization_ms": 800,
    "jd_preprocessing_ms": 900,
    "cv_encoding_ms": 1100,
    "jd_encoding_ms": 1000,
    "scoring_ms": 50,
    "total_ms": 5050
  }
}
```

### Field reference

| Field | Type | Meaning |
|---|---|---|
| `cv_id` | string | MD5 hash of the raw CV text; used as the embedding cache key |
| `match_score`, `match_percentage` | float (0–100) | Final calibrated match percentage (same value, both kept for backward compat) |
| `match_rating` | string | One of: `Excellent Match`, `Good Match`, `Moderate Match`, `Weak Match`, `Poor Match` |
| `recommendation` | string | Plain-language recommendation sentence |
| `confidence` | string | `"high"` (always, since fallback was removed) |
| `overall_similarity` | float (0–100) | Cosine similarity of full-CV ↔ full-JD embeddings × 100 |
| `section_similarities.skills_match` | float (0–100) | Jaccard skill coverage × 100 |
| `section_similarities.skills_semantic` | float (0–100) | Deprecated alias for `skills_match` |
| `section_similarities.experience` | float (0–100) | Experience section cosine × 100 (after boost) |
| `section_similarities.education` | float (0–100) | Education section cosine × 100 (after boost) |
| `raw_scores` | object | 0–1 values of each signal before weighting (use these + the hardcoded `K_WEIGHTS_FULL` weights in the technical guide to recompute the match) |
| `skill_details` | object | Matched/missing/extra skills plus counts |
| `breakdown` | object | Score breakdown with weights as percentages — ready to render |
| `strengths`, `gaps` | array of strings | Auto-generated bullets |
| `cv_summary`, `job_summary` | string | GPT-generated summaries |
| `timing.*_ms` | integer | Per-stage duration in ms |

### Error responses

| Status | Body | When |
|---|---|---|
| 400 | `{"detail": "Unsupported file type"}` | content-type not PDF/DOCX/TXT |
| 400 | `{"detail": "Unable to extract text"}` | extractor returned empty text (scanned PDF, corrupt file) |
| 400 | `{"detail": "Job description is empty"}` | empty `job_description` field |
| 413 | `{"detail": "File too large. Maximum size is 5MB."}` | CV > 5 MB |
| 503 | `{"detail": "Analysis service is temporarily unavailable. Please try again in a moment."}` | OpenAI unavailable, parsing failed, embedding returned None, scoring crashed |

---

## `POST /api/v1/cv/upload`

Upload and parse a CV without matching. Useful for inspecting parser output in isolation.

### Request

`multipart/form-data`:

| Field | Type | Required |
|---|---|---|
| `file` | File | yes (PDF, DOCX, or TXT) |

### Success response — 200 OK

```json
{
  "cv_id": "e3b0c44298fc1c149afbf4c8996fb924",
  "summary": "Senior Python engineer with 5 years of NLP experience...",
  "normalized_skills": ["python", "nlp", "fastapi"],
  "embedding_text": "Senior engineer specialising in NLP pipelines..."
}
```

### Error responses

Same 400 / 503 pattern as `/api/v1/match`.

---

## `POST /api/v1/jd/preprocess`

Preprocess a job description without running a match.

### Request

`application/json`:

```json
{
  "text": "We are hiring a Python engineer..."
}
```

### Success response — 200 OK

```json
{
  "original_text": "...",
  "cleaned_text": "...",
  "required_skills": ["python", "nlp"],
  "preferred_skills": ["docker"],
  "experience_years": "3+ years",
  "education_level": "Bachelor's",
  "experience_requirements": "3+ years of production Python...",
  "education_requirements": "Bachelor's degree in CS or related field",
  "key_phrases": ["python engineer", "nlp pipeline"],
  "summary": "The role focuses on owning the NLP pipeline..."
}
```

### Error responses

| Status | Body |
|---|---|
| 400 | `{"detail": "Job description is empty"}` |
| 503 | `{"detail": "Analysis service is temporarily unavailable..."}` |

---

## CORS

Configured via the `ALLOWED_ORIGINS` env var (comma-separated):

```
ALLOWED_ORIGINS=http://localhost:3000,https://cvmatch.example.com
```

Default: `http://localhost:3000`.

Methods allowed: `GET`, `POST`. Credentials allowed.

---

## Rate limiting

No rate limiting is enforced by the backend. Add one (e.g. `slowapi`) before deploying publicly.
