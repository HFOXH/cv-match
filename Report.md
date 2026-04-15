# CVMatch: Resume & Job Description Matching System
**Cambrian College — Graduate Certificate in Artificial Intelligence / Natural Language Processing — Final Project**

**Authors:** Santiago Cárdenas & Amel Sunil
**Date:** 2026-04-15
**GitHub:** https://github.com/HFOXH/cv-match

---

## 1. Purpose

**Problem definition.** In modern hiring processes, candidates struggle to objectively assess how well their resume aligns with a given job description. Manual comparison of skills, experience, and qualifications is time-consuming and subjective, leading to inefficient applications and missed opportunities on both sides of the hiring table.

**Motivation.** Roughly three-quarters of resumes are rejected by Applicant Tracking Systems before a human reviewer ever reads them. Candidates have no objective way to self-check their fit for a role before submitting. An automated, transparent matching system can help candidates tailor their applications and decide which postings are worth pursuing.

**Objective.** Develop a fully functional, end-to-end NLP system that accepts a CV (PDF, DOCX, or TXT) and a job description, computes a calibrated match percentage, and returns an auditable breakdown — matched skills, missing skills, and a recommendation — in under three seconds.

---

## 2. Solution Approach

**Methodology.** The system follows a modular pipes-and-filters pipeline. Each stage has one responsibility, one input, and one output, and can be replaced without modifying its neighbors.

| Step | Stage | Method |
|------|-------|--------|
| 1 | Extract | pdfplumber · python-docx · chardet |
| 2 | Parse CV | GPT-4o-mini with JSON-mode output |
| 3 | Normalize CV | GPT-4o-mini — dedupe + abbreviation expansion |
| 4 | Preprocess JD | Text cleaner + GPT-4o-mini extraction |
| 5 | Embed sections | OpenAI text-embedding-3-small (1536-dim) + SQLite cache |
| 6 | Score | Jaccard + fuzzy + semantic reconciliation + cosine + boosts + sigmoid |

**NLP techniques employed.**

- **Structured LLM extraction** — GPT-4o-mini with `response_format={"type": "json_object"}` produces reliable structured output across any CV format.
- **Section-level embeddings** — four separate 1536-dim vectors per side (skills, experience, education, overall) enable fine-grained, explainable matching rather than a single opaque blob.
- **Three-tier skill matching** — exact set intersection, then fuzzy (`SequenceMatcher.ratio() ≥ 0.8`), then GPT semantic reconciliation only when unmatched skills remain. Cost-ordered so expensive tiers run least often.
- **Sigmoid calibration** centered at 0.30 stretches raw similarity (which clusters in 0.3–0.8) onto an intuitive 0–100% scale, so a raw 0.45 displays as ≈83%.

**Design principle: fail-loud over fail-wrong.** If any stage cannot produce meaningful signal (OpenAI unavailable, empty text, missing embeddings), the system returns HTTP 503 with a retry message — never a fabricated score.

---

## 3. Technical Implementation & Architecture

**Tech stack.**

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16 · TypeScript · Tailwind CSS · Clerk auth |
| Backend / API | FastAPI (Python 3.11) · Swagger at `/docs` |
| LLM | GPT-4o-mini (parse · normalize · JD extract · semantic reconcile) |
| Embeddings | OpenAI text-embedding-3-small (1536-dim) |
| Math | NumPy · scikit-learn cosine similarity |
| Persistence | SQLite (per-CV embedding cache) |
| Testing | pytest |
| Deployment | Docker + docker-compose |

**Architecture.** A layered modular monolith: **Presentation** (Next.js pages + FastAPI routes) → **Application** (`services/`) → **Domain** (`cv_processor`, `nlp_preprocessing`, `embedding`) → **Infrastructure** (`config.py`, `prompts.py`, middleware). External dependencies (OpenAI, SQLite) sit at the bottom. Every OpenAI call is wrapped in exponential-backoff retry; every route stage is wrapped in specific exception handling that returns 400 for bad input and 503 for service failures.

*Figure 1 — architecture diagram embedded below in the DOCX version of this report.*

**Key design choices.**

- **Centralized configuration.** Every tunable constant (model names, scoring weights, sigmoid parameters, file limits) lives in `config.py`, env-overridable.
- **Centralized prompts.** All seven OpenAI prompts live in `prompts.py` — one file to audit, tune, or A/B test.
- **One deployable process.** A single `docker compose up` boots frontend, backend, and the embedding cache. No orchestration overhead.

---

## 4. Core Functionalities

**Scoring formula.** The final match percentage is a weighted blend of five signals:

| Signal | Weight | Method |
|---|---|---|
| Overall semantic | 30% | Cosine(cv.overall, jd.overall) |
| Skills keyword | 25% | Jaccard + fuzzy + GPT reconciliation |
| Experience match | 25% | Cosine + job-title overlap boost |
| Skills semantic | 10% | Cosine(cv.skills, jd.skills) |
| Education match | 10% | Cosine + education-level ladder boost |

Weights sum to 1.0. The raw weighted sum is passed through `1 / (1 + exp(−8 · (x − 0.30)))` to produce the displayed percentage.

**Model selection rationale.** GPT-4o-mini was chosen for structured extraction because rule-based parsers fail on CV formatting variance; fine-tuning a local model would require substantial labeled data the project did not have. OpenAI's text-embedding-3-small provides deep contextual meaning and handles paraphrasing without additional training. Section-level embeddings, rather than a single flat vector, were essential for producing the explainable breakdown that reviewers see on the analyzer page.

**Design trade-offs.**

- **API cost vs. parsing reliability** — up to six OpenAI calls per cold match, but a SQLite cache keyed on MD5 of the raw CV text skips parsing and embedding on repeat matches, dropping subsequent analyses to roughly two-to-three calls.
- **Fail-loud vs. graceful degradation** — an earlier TF-IDF fallback was removed after observing that it produced a 9.6% match on a clearly-fitting CV. TF-IDF on full-text resumes versus JDs rarely shares literal words even when the semantic fit is strong. We replaced the fallback with HTTP 503 and a clear retry message: a wrong number is worse than no number.
- **Modularity vs. boilerplate** — the backend is split into ten modules with explicit service wrappers. The boilerplate cost is low; the payoff is that post-submission refactors (centralizing config, removing TF-IDF, adding live UI breakdown) were clean, localized changes.

---

## 5. Result Analysis — Engineering Outcomes & System Behavior

Rather than report benchmark accuracy on a labeled test set (a reproducible evaluation harness is listed under future work), this section documents concrete, measurable properties of the shipped system — each one verifiable by reading the source or running a live request against the deployed service.

| Observation | How it is verified |
|---|---|
| Cold match ~2.1 s · cached match ~0.5 s | `timing` object returned in every `/api/v1/match` response |
| Up to 6 OpenAI calls per cold match · 2–3 with warm cache | Code inspection of `routes/match.py` + `hybrid_encoder.py` |
| 4 × 1536-dim embeddings per CV / JD (skills, experience, education, overall) | `SectionEmbeddingGenerator` |
| Skills extracted from all CV sections, not only a "Skills" header | Prompt `K_CV_PARSER_USER_PROMPT` in `prompts.py` |
| Sigmoid maps raw 0.45 → 83% calibrated | `SimilarityEngine.calibrate_score` |
| Missing `OPENAI_API_KEY` → HTTP 503, never a fabricated score | Reproducible by unsetting the key and calling the API |
| SQLite cache auto-discards stale rows where `overall=None` | `HybridEncoder.encode_cv` guard block |

**Interpretation.** The project's central engineering decision was *fail-loud over fail-wrong.* During development we observed a removed TF-IDF fallback produce a 9.6% score for a CV and JD that were a clearly-strong fit. Rather than ship a resilience feature that misleads users, we removed the fallback and accept that a very small reliability window is the correct trade for user trust. The SQLite cache — keyed by MD5 of the raw CV text — reduces iterative-use cost substantially; a user comparing one CV against several JDs gets sub-second responses after the first match.

**Key findings.**

1. Structured LLM parsing handles CV format variance that rule-based parsers cannot.
2. Section-level embeddings enable the live, auditable breakdown rendered in the UI — reviewers see the math, not a black-box number.
3. Centralized configuration and prompts kept post-submission refactors reviewable rather than scattered.
4. Fail-loud is a feature: HTTP 503 with a retry message is preferable to a misleading percentage.

**Future work.** A formal evaluation harness with labeled CV–JD pairs; async route handlers and Postgres/pgvector for multi-tenant scaling; OCR support for image-only PDFs; streaming partial pipeline results to the UI.
