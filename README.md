# CVMatch

 An AI-powered system that scores how well your resume matches any job description, shows exactly where you fit and where you don't, and explains how the score was calculated.

**Authors:** Santiago Cárdenas & Amel Sunil
**Stack:** FastAPI · Next.js · OpenAI (GPT-4o-mini + text-embedding-3-small) · Tailwind · Clerk

---

## What it does

Upload a CV and paste a job description. CVMatch returns:

- A calibrated **match percentage** (0–100)
- A **skill breakdown** — matched, missing, extra (keyword + fuzzy + semantic reconciliation)
- **Section-level similarity** for skills, experience, education, and overall semantic fit
- A **live calculation view** showing exactly how each signal contributed to the final score
- A **recommendation** bucket (Excellent / Good / Moderate / Weak / Poor)

---

## Quick start with Docker (recommended)

```bash
# 1. Copy env template and fill in your keys
cp .env.example .env

# 2. Build and run both services
docker compose up --build

# 3. Open http://localhost:3000
```

Required env vars (see `.env.example`):

| Variable | Where it goes | Notes |
|---|---|---|
| `OPENAI_API_KEY` | Backend runtime | Used for parsing, normalization, embeddings |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Frontend **build time** | Baked into client bundle |
| `CLERK_SECRET_KEY` | Frontend runtime | Server-side only |

> ℹ️ If you change the Clerk publishable key, rebuild the frontend image — it's baked in at build time.

## Local development without Docker

See [`docs/DEVELOPMENT.md`](./docs/DEVELOPMENT.md) for running the backend (`uvicorn`) and frontend (`npm run dev`) separately.

---

## Documentation

| Doc | What's in it |
|---|---|
| [User guide](./docs/USER_GUIDE.md) | How to use the app end-to-end |
| [Technical guide](./docs/TECHNICAL_GUIDE.md) | How the scoring engine works under the hood — weights, calibration, boosts |
| [API reference](./docs/API.md) | Every backend endpoint, request/response shapes, error codes |
| [Development](./docs/DEVELOPMENT.md) | Running locally, environment, tests, common tasks |

Live explanation of the scoring logic is also available in the running app at **[`/scoring`](http://localhost:3000/scoring)**.

---

## Architecture at a glance

```
┌────────────────┐         ┌──────────────────────────────────────────┐
│   Next.js UI   │  HTTP   │              FastAPI backend              │
│  (port 3000)   │ ──────► │                 (port 8000)               │
└────────────────┘         │                                            │
                           │  Upload → Extract → Parse (GPT)            │
                           │        → Normalize (GPT)                   │
                           │        → Embed sections (OpenAI embeddings)│
                           │        → Score (Jaccard + cosine + boosts) │
                           │        → Calibrate (sigmoid)               │
                           └──────────────────┬─────────────────────────┘
                                              │
                                              ▼
                                        ┌──────────┐
                                        │  OpenAI  │
                                        │   API    │
                                        └──────────┘
```

Top-level layout:

```
cv-match/
├─ backend/            # FastAPI app, scoring engine, pipeline modules
├─ frontend/           # Next.js app
├─ docs/               # User, technical, API, development guides
├─ docker-compose.yml
├─ .dockerignore
└─ .env.example
```

For a full directory tree and per-module descriptions, see [`docs/TECHNICAL_GUIDE.md`](./docs/TECHNICAL_GUIDE.md#project-structure).

---

## Common commands

```bash
# Start everything (Docker)
docker compose up -d

# Tail backend logs
docker compose logs -f backend

# Stop
docker compose down

# Rebuild after code changes
docker compose up --build

# Open FastAPI auto-docs
open http://localhost:8000/docs
```

---

## Troubleshooting

**"Analysis service is temporarily unavailable" on every request**
→ Your `OPENAI_API_KEY` is missing, invalid, or out of quota. Check `docker compose logs backend` for the real error.

**Frontend loads but Clerk crashes**
→ `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` wasn't set when the image was built. Run `docker compose up --build`.

**Low match % for a good CV**
→ Check the "How 87% was calculated" card on the analyzer page — it breaks down every signal. Most common cause is OpenAI extracting very few skills from a scanned/image-only PDF.

---

## License

Released under the [MIT License](./LICENSE) — free to use, modify, and distribute with attribution.
