# Development guide

Running CVMatch locally without Docker, plus the everyday developer tasks.

---

## Prerequisites

- **Python** 3.11+ (3.12 works too)
- **Node.js** 20+ and npm
- An **OpenAI API key** with credit
- A **Clerk** project with publishable + secret keys (free tier is fine)

---

## First-time setup

### 1. Clone and create env files

```bash
git clone <repo-url> cv-match
cd cv-match
cp .env.example .env
# Edit .env and fill in your OPENAI_API_KEY, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
./venv/Scripts/activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend

```bash
cd ../frontend
npm install
```

---

## Running (two terminals)

**Terminal 1 — backend:**

```bash
cd backend
# Activate venv (see above), then:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for the FastAPI auto-docs.

**Terminal 2 — frontend:**

```bash
cd frontend

# For Clerk to work, export the env vars your shell session (or use a .env.local
# inside frontend/):
export NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
export CLERK_SECRET_KEY=sk_test_...

npm run dev
```

Open `http://localhost:3000`.

> 💡 On Windows bash, use `set VAR=value` or add the vars to `frontend/.env.local`.

---

## Environment variables

| Variable | Consumer | Required | Default |
|---|---|---|---|
| `OPENAI_API_KEY` | Backend | ✅ | — |
| `ALLOWED_ORIGINS` | Backend (CORS) | | `http://localhost:3000` |
| `LOG_TO_FILE` | Backend logging | | unset (stdout only) |
| `LOG_DIR` | Backend logging | | `backend/logs/` (when LOG_TO_FILE=1) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Frontend (build time) | ✅ | — |
| `CLERK_SECRET_KEY` | Frontend (runtime) | ✅ | — |
| `NEXT_PUBLIC_BACKEND_URL` | Frontend (optional) | | `http://localhost:8000` |

Set `LOG_TO_FILE=1` in local dev to mirror stdout logs into `backend/logs/app.log` (rotates at 5 MB, keeps 5 files).

---

## Project layout for contributors

See [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md#project-structure) for the full directory tree with module descriptions.

Key files when you're making changes:

| Change | File |
|---|---|
| Tweak scoring weights / calibration | `backend/services/similarity_engine.py` |
| Edit an OpenAI prompt | `backend/prompts.py` |
| Add a new route | `backend/routes/` + register in `backend/api/main.py` |
| Change file type support | `backend/cv_processor/extractors/` |
| Add frontend page | `frontend/app/<route>/page.tsx` |
| Edit navbar / footer | `frontend/components/Navbar.tsx`, `Footer.tsx` |

---

## Tests

```bash
cd backend
pytest -v
```

> ⚠️ Known issue: the test suite has a pre-existing circular import (between `services/__init__.py` and `cv_processor/__init__.py`) that prevents most tests from being collected in some run orders. This is tracked for cleanup. The production app is unaffected.

OpenAI calls are mocked in tests — no API credits are spent.

### What's covered

- `test_cleaner.py` — `TextCleaner.normalize_skills` (exact / fuzzy / dedupe / None-safe / non-string safe)
- `test_cv_normalizer.py` — CV normalization pipeline
- `test_job_preprocessor.py` — JD preprocessing pipeline
- `test_openai_encoder.py` — encoder wrapper
- `test_openai_parser.py` — CV parser
- `test_section_embeddings.py` — per-section embedding generation
- `test_vector_store.py` — SQLite cache
- `test_hybrid_encoder.py` — orchestration
- `test_similarity_engine.py` — scoring (Jaccard, calibration, sigmoid, banding)
- `test_request_logger.py` — middleware

### Known broken tests

After the fallback-removal refactor, some tests still reference removed symbols (`fallback_parse`, `K_WEIGHTS_FALLBACK`, `tfidf_sim`). These tests need to be rewritten. Production code doesn't use any of these.

---

## Common tasks

### Edit a prompt

All prompts live in `backend/prompts.py`. Every consumer imports the constants; edit in one place.

### Change scoring weights

`backend/services/similarity_engine.py` → `K_WEIGHTS_FULL`. They must sum to 1.0.

Don't forget to update the UI display in two places:

- `frontend/app/analyzer/page.tsx` — the "How X% was calculated" card
- `frontend/app/scoring/page.tsx` — the `/scoring` explainer

### Change the sigmoid calibration

`K_SIGMOID_STEEPNESS` and `K_SIGMOID_MIDPOINT` in `similarity_engine.py`. Also update the table on `/scoring`.

### Clear the embedding cache

```bash
rm backend/vectors.db
```

Or in Docker:

```bash
docker compose down
docker compose up --build
```

### Add a new file format

1. Add an extractor in `backend/cv_processor/extractors/<format>_extractor.py` with an `extract()` method
2. Register it in `backend/cv_processor/processor.py` `K_SUPPORTED_FORMATS`
3. Add the MIME type to `backend/services/cv_service.py` `ALLOWED_TYPES`

---

## Debugging

### Backend logs

If running with `--reload`, logs print to your uvicorn terminal.
If `LOG_TO_FILE=1`, also appended to `backend/logs/app.log`.

Every request logs one line:
```
2026-04-13 04:23:01,789 | INFO | middleware.request_logger | POST /api/v1/match | 200 | 4023ms | 127.0.0.1
```

Full tracebacks on errors use `logger.exception(...)`.

### Frontend

```javascript
// analyzer/page.tsx already logs the full backend response:
console.log("[match] backend response:", r);
```

Open your browser's DevTools → Console to see it after a match.

### Inspect the embedding cache

```bash
cd backend
sqlite3 vectors.db
sqlite> .schema cv_vectors
sqlite> SELECT cv_id, skills_list FROM cv_vectors;
```

---

## Code style

- **Python**: no linter configured — keep to reasonable PEP 8. Use `logger.exception(...)` for error paths. Defensive type checks at input boundaries.
- **TypeScript / React**: Next.js 16 + ESLint 9 defaults. Run `npm run lint` from `frontend/`.

---

## Making API changes

1. Add / edit the route in `backend/routes/`
2. Update the frontend consumer (usually `frontend/app/analyzer/page.tsx`)
3. Update the [`API.md`](./API.md) doc

The frontend reads fields directly from the response; there's no generated client. Keep field names stable when in doubt.

---

## Release checklist (before deploying to real users)

CVMatch is currently set up for local/Docker use. Before exposing to the internet, at minimum:

- [ ] Switch `http://localhost:8000` in `frontend/app/analyzer/page.tsx:101` to `process.env.NEXT_PUBLIC_BACKEND_URL`
- [ ] Add rate limiting on `/api/v1/match` (e.g. `slowapi`)
- [ ] Tighten `CORSMiddleware.allow_headers` from `["*"]` to an explicit list
- [ ] Validate `ALLOWED_ORIGINS` at startup
- [ ] Add a persistent volume for `vectors.db` or migrate to Postgres/pgvector for multi-instance deployment
- [ ] Async routes (convert `match_cv_with_jd` to `async def` + `run_in_executor`) — required under any real concurrency
- [ ] SQLite cache locking or migrate off SQLite entirely
- [ ] Remove test files' references to removed symbols; re-enable CI
- [ ] Resolve the pre-existing circular import (`services/__init__.py` ↔ `cv_processor/__init__.py`)
