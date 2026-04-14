# Technical guide

How CVMatch actually works — the pipeline, the scoring engine, the weights, and the data flow. Written for developers and contributors.

---

## Project structure

```
cv-match/
├── backend/
│   ├── api/
│   │   └── main.py                    # FastAPI entrypoint, CORS, logging config
│   ├── routes/
│   │   ├── match.py                   # POST /api/v1/match — main pipeline
│   │   ├── cv.py                      # POST /api/v1/cv/upload
│   │   └── job_description.py         # POST /api/v1/jd/preprocess
│   ├── cv_processor/
│   │   ├── processor.py               # CVProcessor: extract → parse
│   │   ├── extractors/                # PDF / DOCX / TXT text extraction
│   │   └── parsers/
│   │       └── openai_parser.py       # GPT-4o-mini structured parse
│   ├── nlp_preprocessing/
│   │   ├── cleaner.py                 # TextCleaner (strip URLs, normalize whitespace, dedupe skills)
│   │   ├── cv_normalizer.py           # CVDataNormalizer — GPT normalization pass
│   │   └── job_preprocessor.py        # JobDescriptionPreprocessor — GPT JD extraction
│   ├── embedding/
│   │   ├── openai_encoder.py          # text-embedding-3-small wrapper
│   │   ├── section_embeddings.py      # Build per-section embeddings from structured data
│   │   ├── vector_store.py            # SQLite cache for CV vectors
│   │   └── hybrid_encoder.py          # Orchestrator for CV & JD encoding
│   ├── services/
│   │   ├── cv_service.py              # Upload → extract → parse wrapper
│   │   ├── normalization_service.py   # CV normalizer wrapper
│   │   ├── job_description_service.py # JD preprocessor wrapper
│   │   ├── matching_service.py        # Encode + compute match
│   │   ├── similarity_engine.py       # Core scoring logic
│   │   └── openai_retry.py            # Exponential-backoff retry for OpenAI calls
│   ├── middleware/
│   │   └── request_logger.py          # Per-request log line (method, path, status, latency)
│   ├── prompts.py                     # Central registry of all OpenAI prompts
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # Landing page
│   │   ├── analyzer/page.tsx          # Main analyzer UI
│   │   ├── scoring/page.tsx           # /scoring — full scoring explainer
│   │   ├── privacy/ terms/ support/   # Static pages
│   │   ├── layout.tsx, providers.tsx, globals.css
│   │   └── proxy.ts
│   ├── components/
│   │   ├── Navbar.tsx, Footer.tsx, ThemeToggle.tsx
│   │   ├── Paywall.tsx, FeatureComparison.tsx, MatchCircle.tsx
│   ├── Dockerfile
│   ├── next.config.ts                 # output: "standalone"
│   └── package.json
├── docs/                              # This folder
├── docker-compose.yml
├── .dockerignore
└── .env.example
```

---

## End-to-end pipeline

A single `POST /api/v1/match` triggers six stages. Each is timed and returned in the response's `timing` object.

```
┌────────────────────────────────────────────────────────────────────┐
│  1. Extract & parse CV  (routes/match.py → cv_processor)           │
│     • Extractor converts PDF/DOCX/TXT → raw text                   │
│     • OpenAICVParser uses GPT-4o-mini (JSON mode) to produce       │
│       structured: contact, skills, experience, education, summary  │
│       education_level                                              │
│  ─────────────────────────────────────────────────────────────     │
│  2. Normalize CV  (nlp_preprocessing/cv_normalizer)                │
│     • GPT-4o-mini pass: dedupes + lowercases skills, expands       │
│       abbreviations, generates experience_text / education_text /  │
│       full_text_for_embedding (comparison-ready paragraphs)        │
│  ─────────────────────────────────────────────────────────────     │
│  3. Preprocess JD  (nlp_preprocessing/job_preprocessor)            │
│     • Mechanical text cleaning (URLs, whitespace)                  │
│     • GPT-4o-mini extracts: required_skills, preferred_skills,     │
│       experience_years, education_level, key_phrases, summary,     │
│       experience_requirements, education_requirements              │
│  ─────────────────────────────────────────────────────────────     │
│  4. Embed CV sections  (embedding/section_embeddings)              │
│     • text-embedding-3-small produces 1536-dim vectors for:        │
│       skills, experience, education, overall                       │
│     • Cached in SQLite (vectors.db) keyed by MD5 of raw text       │
│  ─────────────────────────────────────────────────────────────     │
│  5. Embed JD sections                                              │
│     • Same four slots for the job description side                 │
│  ─────────────────────────────────────────────────────────────     │
│  6. Match & score  (services/similarity_engine)                    │
│     • Jaccard + fuzzy skill matching                               │
│     • Optional GPT semantic reconciliation for missing skills      │
│     • Cosine similarity on section embeddings                      │
│     • Education & experience heuristic boosts                      │
│     • Sigmoid calibration → final 0–100%                           │
└────────────────────────────────────────────────────────────────────┘
```

If any stage can't produce meaningful signal (OpenAI is down, parse returns nothing useful, overall embedding is missing), the route returns **HTTP 503** with a clear message. There is no fallback scoring path — we refuse to show a misleading number.

---

## The scoring engine

Located in `backend/services/similarity_engine.py`. Walk through what happens when `calculate_match(cv_vectors, jd_vectors)` is called.

### Weights

```python
K_WEIGHTS_FULL = {
    "skills_jaccard":   0.25,   # Keyword + fuzzy skill coverage
    "skills_semantic":  0.10,   # Cosine on skill-section embeddings
    "sbert_overall":    0.30,   # Cosine on full-CV ↔ full-JD embeddings
    "experience_match": 0.25,   # Cosine + job-title boost
    "education_match":  0.10,   # Cosine + education-level boost
}
```

They sum to 1.0. Skills (25+10 = 35%) and overall semantic (30%) carry the most weight because they're the most reliable signals.

### Step 1 — skill keyword matching (Jaccard-ish)

`calculate_jaccard(cv_skills, jd_skills)`:

1. Lowercase + strip both sets
2. **Exact** intersection
3. **Fuzzy** match on leftovers — word-boundary substring OR `SequenceMatcher.ratio() ≥ 0.8`
4. `score = matched / |jd_set|` (recall, not true Jaccard — extra CV skills are not penalized)

Returns `{score, matched_skills, missing_skills, extra_skills, counts}`.

### Step 2 — semantic skill reconciliation (optional)

If skills remain in both `missing_skills` (JD side) and `extra_skills` (CV side), call GPT-4o-mini with both lists and ask it to pair equivalents:

```
"teamwork" ↔ "interpersonal skills"
"stock rotation" ↔ "inventory management"
```

Newly paired skills move from missing → matched, and the score is recomputed. This is the "skills_semantic" signal's partner on the explanation side — the raw cosine value itself is computed separately from embeddings.

### Step 3 — section similarity

`_section_similarities(cv_vectors, jd_vectors)`:

```python
skills_semantic = cosine(cv.skills_embedding, jd.skills_embedding)
experience     = cosine(cv.experience_embedding, jd.experience_embedding  OR  jd.overall)
education      = cosine(cv.education_embedding,  jd.education_embedding   OR  jd.overall)
sbert_overall  = cosine(cv.overall_embedding,    jd.overall_embedding)
```

Each `cosine()` is defensive: None vectors → 0.0, NaN/Inf → 0.0, shape mismatch → 0.0, log a warning.

### Step 4 — education boost

`_education_score(semantic_sim, cv_edu, jd_edu)`:

```
PhD > Master > Bachelor > Diploma > High School      (levels 5 → 1)

if cv_level >= jd_level      → max(semantic_sim, 0.8)
elif cv_level == jd_level-1  → max(semantic_sim, 0.5)
else                         → semantic_sim
```

Protects candidates who meet the degree bar but whose institution wording doesn't semantically match the JD phrasing.

### Step 5 — experience boost

`_experience_score(semantic_sim, cv_titles, jd_title)`:

```
substring hit between cv_title and jd_title → max(sim, 0.85)
word overlap ≥ 50%                          → max(sim, 0.75)
word overlap ≥ 25%                          → max(sim, 0.60)
otherwise                                    → sim
```

JD "job title" is taken as the first key phrase (since JDs don't have a clean title field).

### Step 6 — weighted sum

```python
raw_scores = {
    "skills_jaccard":   skill_details["score"],
    "skills_semantic":  section_sims["skills_semantic"],
    "sbert_overall":    cosine(overall, overall),
    "experience_match": experience_score,
    "education_match":  education_score,
}
weighted_sum = Σ raw_scores[k] × K_WEIGHTS_FULL[k]      # in [0, 1]
```

### Step 7 — sigmoid calibration

Raw similarities cluster in 0.3–0.8; a raw cosine of 0.45 is actually a solid match but "45%" reads as weak. A sigmoid centered at 0.30 stretches the meaningful range to 0–100:

```python
K_SIGMOID_STEEPNESS = 8
K_SIGMOID_MIDPOINT  = 0.30

calibrated = 1 / (1 + exp(-8 · (raw − 0.30)))
percentage = round(calibrated × 100, 1)
```

| raw  | calibrated |
|------|------------|
| 0.10 | 15%        |
| 0.30 | 50%        |
| 0.50 | 83%        |
| 0.70 | 96%        |
| 0.90 | 99%        |

### Step 8 — banding

`get_score_band(percentage)` maps to one of:

| Range   | Rating          |
|---------|-----------------|
| 90–100  | Excellent Match |
| 75–90   | Good Match      |
| 60–75   | Moderate Match  |
| 40–60   | Weak Match      |
| 0–40    | Poor Match      |

---

## Embedding cache

`backend/embedding/vector_store.py` — a single SQLite table `cv_vectors`:

```sql
cv_id TEXT PRIMARY KEY,              -- MD5 hash of raw CV text
overall_embedding BLOB,              -- 1536-dim float32 vector
skills_embedding BLOB,
experience_embedding BLOB,
education_embedding BLOB,
skills_list TEXT,                    -- JSON
raw_text_hash TEXT,
is_fallback INTEGER DEFAULT 0,       -- legacy, always 0 now
created_at TIMESTAMP
```

Cache is read before generating embeddings. Entries without a valid `overall_embedding` are discarded and regenerated automatically — this auto-cleans stale rows from before the fallback-removal refactor.

The DB lives at `/app/vectors.db` inside the backend container and is not persisted across `docker compose down` by default. First match on a given CV re-embeds; subsequent matches on the same CV are fast.

---

## Prompts

All seven OpenAI prompts live in `backend/prompts.py`:

| Constant | Used by |
|---|---|
| `K_CV_PARSER_SYSTEM_PROMPT`, `K_CV_PARSER_USER_PROMPT` | `cv_processor/parsers/openai_parser.py` |
| `K_NORMALIZATION_SYSTEM_PROMPT`, `K_NORMALIZATION_USER_PROMPT` | `nlp_preprocessing/cv_normalizer.py` |
| `K_EXTRACTION_SYSTEM_PROMPT`, `K_EXTRACTION_USER_PROMPT` | `nlp_preprocessing/job_preprocessor.py` |
| `K_SEMANTIC_MATCH_PROMPT` | `services/similarity_engine.py` |

Edit them here; all call sites import the constants directly. Placeholders use `str.format()` style (`{cv_text}`, `{jd_text}`, `{cv_skills}`, etc.); literal JSON braces are doubled to escape them.

---

## Error handling

Each pipeline stage in `routes/match.py` is wrapped in a specific try/except. The response:

- **400** — bad input (empty text, unsupported file type, processing error)
- **413** — file too large (> 5 MB)
- **503** — service unavailable (OpenAI failed, embedding unavailable, scoring crashed)
- **200** — success

The backend never returns a misleading match score on failure — 503 is preferred over a fake number.

Internal errors are logged with `logger.exception(...)` and a generic detail is returned to the client (no stack traces leaked).

---

## OpenAI retry

`backend/services/openai_retry.py` — `retry_openai_call(func, *args, **kwargs)` wraps calls with exponential backoff (1s, 2s, 4s) on `RateLimitError` and other transient errors. Non-retryable errors (auth, bad request) propagate immediately.

---

## Request logging

`backend/middleware/request_logger.py` logs every request as a single line:

```
POST /api/v1/match | 200 | 4012ms | 172.18.0.1
```

---

## Configuration summary

| Env var | Consumer | Default |
|---|---|---|
| `OPENAI_API_KEY` | Backend (parser, normalizer, JD extractor, encoder, similarity engine) | — (required) |
| `ALLOWED_ORIGINS` | Backend CORS | `http://localhost:3000` |
| `LOG_TO_FILE` | Backend logging | unset (stdout only) |
| `LOG_DIR` | Backend logging | `backend/logs/` (when `LOG_TO_FILE=1`) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Frontend (build time) | — (required) |
| `CLERK_SECRET_KEY` | Frontend (runtime) | — (required) |
| `NEXT_PUBLIC_BACKEND_URL` | Frontend (build time) | `http://localhost:8000` |

---

## Why we removed the TF-IDF fallback

An earlier version dropped to a TF-IDF + raw-embedding fallback when OpenAI wasn't available. Observed behavior: a well-matching CV + JD produced a ~9.6% score because TF-IDF on full CV vs full JD is near-random — the docs rarely share literal words. The misleading number was worse than no answer. The fallback was removed in favor of an explicit 503 with a retry message.

If you want to add a resilience layer back, do it above the pipeline (retry the whole request, queue for later), not inside it.
