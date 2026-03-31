# CV-Match Changes Log

## Update 1: Fixed Request Logging (feature/api-logging-timing branch)

**File:** `backend/api/main.py`

**Problem:** The `RequestLoggingMiddleware` was added but the logger `cvmatch.requests` had no handler configured, so log messages were silently dropped.

**Fix:** Added `import logging` and `logging.basicConfig(level=logging.INFO)` to `main.py` so the logger outputs to the console.

**Result:** Backend terminal now shows lines like:
```
INFO:cvmatch.requests:POST /api/v1/match | 200 | 3456ms | 127.0.0.1
```

---

## Update 2: Fixed Scoring Calibration — Jaccard Denominator

**File:** `backend/services/similarity_engine.py`

**Problem:** Jaccard skill matching divided matched skills by the **union** of all CV + JD skills. This penalized candidates for having extra skills not in the JD. For example, matching 2 JD skills out of 9 required, but with 6 extra CV skills, gave 2/15 = 13% instead of 2/9 = 22%.

**Fix:** Changed denominator from `len(union)` to `len(jd_set)` — the score now answers "what percentage of required skills does the candidate have?"

**Lines changed:**
- `calculate_jaccard()`: `score = len(matched) / len(jd_set)`
- `_enhance_with_semantic_matching()`: `score = matched_count / jd_total`

---

## Update 3: Fixed Scoring Calibration — Sigmoid Parameters

**File:** `backend/services/similarity_engine.py`

**Problem:** The sigmoid calibration was too aggressive. With steepness=12 and midpoint=0.45, any raw score below ~0.35 got crushed to near 0%. A realistic CV-JD pair often has a raw weighted score of 0.3-0.5, so moderate matches were being reported as "Poor Match".

**Fix (applied in two steps):**
1. First adjustment: steepness 12 -> 8, midpoint 0.45 -> 0.35 (score went from 18% to 48%)
2. Second adjustment: midpoint 0.35 -> 0.30 (score went from 48% to 68%)

**Final values:** `K_SIGMOID_STEEPNESS = 8`, `K_SIGMOID_MIDPOINT = 0.30`

---

## Update 4: Adjusted Component Weights

**File:** `backend/services/similarity_engine.py`

**Problem:** TF-IDF had 10% weight but only scores ~7% due to a known flaw with 2-document corpora (shared terms get low IDF). Skills Jaccard at 30% was too punishing when keyword mismatches exist but semantics align.

**Fix:** Redistributed weights to favor more reliable signals:

| Component | Before | After |
|---|---|---|
| Skills Jaccard | 30% | 25% |
| Skills Semantic | 10% | 10% |
| Overall Semantic | 25% | 30% |
| Experience Match | 20% | 25% |
| Education Match | 5% | 5% |
| TF-IDF Keywords | 10% | 5% |

---

## Update 5: Made Skill Extraction Industry-Agnostic

**Files:**
- `backend/cv_processor/parsers/openai_parser.py`
- `backend/nlp_preprocessing/cv_normalizer.py`
- `backend/nlp_preprocessing/job_preprocessor.py`
- `backend/services/similarity_engine.py`

**Problem:** All prompts were biased toward IT/tech roles. Examples only mentioned Python, React, Kubernetes, etc. Non-tech CVs (retail, healthcare, trades) had poor skill extraction because the AI was primed for tech skills only.

**Fixes:**

### CV Parser (`openai_parser.py`)
- Updated skill extraction instructions to cover ANY industry
- Added examples: "operated cash register" -> "cash handling", "prepared food items" -> "food preparation"
- Included soft skill inference from experience descriptions
- Added tool/equipment extraction (POS systems, forklift, Excel, SAP)

### CV Normalizer (`cv_normalizer.py`)
- Expanded abbreviation examples beyond tech (POS, CPR, HVAC)
- Added rule to split compound skills ("teamwork and communication" -> "teamwork", "communication")
- Added rule to infer implicit skills from experience (retail work -> multitasking, time management)
- Updated experience_text and education_text examples with non-tech roles
- Added explicit note that rules apply to ALL industries

### JD Preprocessor (`job_preprocessor.py`)
- Updated skill normalization examples for all industries
- Added rule to exclude physical requirements from skills ("ability to stand for extended periods", "ability to lift 50 lbs")
- Added rule to exclude availability requirements from skills
- Updated key phrases examples with non-tech terms
- Updated experience/education requirement examples

### Semantic Skill Matcher (`similarity_engine.py`)
- Broadened matching prompt to be less strict
- Added cross-industry matching examples (stock rotation -> inventory management, cash handling -> POS, patient care -> healthcare delivery)

---

## Update 6: Improved Semantic Skill Matching

**File:** `backend/services/similarity_engine.py`

**Problem:** The semantic matching prompt was too conservative. It missed obvious pairs like "teamwork" matching "interpersonal skills", or "quality control" matching "attention to detail".

**Fix:** Updated the prompt with more permissive matching rules and diverse examples. A CV skill that "demonstrates" the JD requirement now counts as a match, not just exact equivalents.

---

## Score Impact Summary

Testing with a retail CV (Store Associate, 2+ years at No Frills) against a Retail Store Associate JD:

| Metric | Before All Changes | After All Changes |
|---|---|---|
| Match Score | 18.3% | 83.3% |
| Rating | Poor Match | Good Match |
| Skills Matched | 2/9 | 6/11 |
| Recommendation | Not recommended | Apply with confidence |

---

## Update 7: Removed TF-IDF from Full Mode Scoring

**Files:**
- `backend/services/similarity_engine.py`
- `backend/services/matching_service.py`

**Problem:** TF-IDF only scored ~7% even for strong matches because it's fundamentally unreliable with only 2 documents — shared terms get low IDF scores since they appear in "50% of the corpus". This was dragging down every match score.

**Fix:**
- Removed `tfidf_overall` from `K_WEIGHTS_FULL` (full mode scoring)
- Removed TF-IDF from the breakdown report
- Redistributed the 5% weight to education (5% -> 10%)
- TF-IDF is still used in **fallback mode** (when parsing fails) since there's no structured data available, but reduced weight from 45% to 30%

**New weights (full mode):**

| Component | Before | After |
|---|---|---|
| Skills Jaccard | 25% | 25% |
| Skills Semantic | 10% | 10% |
| Overall Semantic | 30% | 30% |
| Experience Match | 25% | 25% |
| Education Match | 5% | 10% |
| TF-IDF Keywords | 5% | REMOVED |

**Fallback mode weights:** Semantic 55% -> 70%, TF-IDF 45% -> 30%

---

## Update 8: Smart Education Scoring

**Files:**
- `backend/services/similarity_engine.py`
- `backend/routes/match.py`

**Problem:** Education scoring was pure cosine similarity between embeddings. A candidate with a college diploma applying for a job requiring a high school diploma scored ~24% on education — even though they *exceed* the requirement. The embeddings don't understand hierarchical relationships.

**Fix:** Added education level comparison logic:
- Defined education hierarchy: High School (1) < Diploma/Associate (2) < Bachelor's (3) < Master's (4) < PhD (5)
- If candidate **meets or exceeds** the requirement: score is at least 0.8 (80%)
- If candidate is **one level below**: score is at least 0.5 (50%)
- Otherwise: falls back to semantic similarity
- Education levels are extracted from parsed CV data and JD preprocessing, then passed through to the similarity engine via `cv_vectors["education_level"]` and `jd_vectors["education_level"]`

**New method:** `_education_score()` with `_parse_education_level()` helper

---

## Update 9: Filter Physical Requirements from JD Skills

**File:** `backend/nlp_preprocessing/job_preprocessor.py`

**Problem:** The JD skill extractor was pulling physical requirements like "ability to stand for extended periods" and "ability to lift light to moderate loads" into the skills list. These aren't skills — they're working conditions. Having them as "missing skills" unfairly penalized candidates and inflated the missing skills count.

**Fix:** Added two rules to the JD extraction prompt:
- Do NOT include physical requirements as skills (standing, lifting, cold environments, physical stamina)
- Do NOT include generic availability requirements as skills (flexible schedule, available weekends)

---

## Score Impact Summary

Testing with a retail CV (Store Associate, 2+ years at No Frills) against a Retail Store Associate JD:

| Metric | Original | After Updates 1-6 | After Updates 7-9 |
|---|---|---|---|
| Match Score | 18.3% | 83.3% | TBD (retest needed) |
| Rating | Poor Match | Good Match | TBD |
| Skills Matched | 2/9 | 6/11 | TBD (fewer false missing) |
| Education Score | ~24% | ~32% | Expected ~80%+ |

---

## Update 10: Fixed Education Level Parsing

**File:** `backend/services/similarity_engine.py`

**Problem:** The education level parser failed to recognize degrees like "Software engineering technology" because it only looked for exact keywords like "diploma" or "bachelor". Also, the keyword matching was unordered — "high school diploma" could match "diploma" (level 2) before "high school" (level 1).

**Fix:**
- Changed `K_EDUCATION_LEVELS` from a flat dict to an ordered list (highest level first)
- Added many more keywords: "technology", "technologist", "technician", "certificate", "vocational", "polytechnic", "postgraduate", "post-graduate", "b.sc", "b.eng", etc.
- Parser now checks PhD first, then Master's, then Bachelor's, etc. — so "high school diploma" correctly matches "high school" (level 1) not "diploma" (level 2)

**Impact:** A CV with "Software engineering technology" from a college now correctly gets level 2 (college/diploma), which exceeds "high school" (level 1) → education score boosted from ~32% to 80%+

---

## Update 11: Standardized Education Level From GPT

**Files:**
- `backend/cv_processor/parsers/openai_parser.py`
- `backend/routes/match.py`

**Problem:** Education level was being guessed from free-text degree names using keyword matching. Since GPT-4o-mini can return the same degree differently each time ("Software Engineering Technology" vs "Diploma in Software Engineering"), keyword matching was unreliable.

**Fix:** Added `education_level` to the CV parser schema with a constrained set of values:
- GPT now returns one of: `"phd"`, `"masters"`, `"bachelors"`, `"college diploma"`, `"high school"`, or `null`
- The match route now reads this standardized field directly instead of joining degree names and guessing
- The keyword-based `_parse_education_level()` still works as a fallback to parse these standardized values

**Result:** Education level detection is now consistent regardless of how GPT phrases the degree name.

---

## Update 12: Removed TF-IDF From Frontend and Cleaned Backend

**Files:**
- `frontend/app/page.tsx`
- `backend/routes/match.py`
- `backend/services/matching_service.py`

**Problem:** TF-IDF was removed from the scoring weights in Update 7, but it was still being computed, returned in the API response, and displayed as "Keyword Match" in the frontend (showing ~7% which confused users).

**Fix:**
- **Frontend:** Removed `tfidfSimilarity` state variable, removed the setter call, and removed the "Keyword Match" progress bar from the Score Breakdown section
- **Backend route:** Removed `tfidf_similarity` from the API response
- **Backend matching service:** TF-IDF is now only computed in fallback mode (when CV parsing fails). In full mode, it's skipped entirely — saving one computation step

**Result:** The Score Breakdown now shows only the 4 meaningful metrics: Overall Semantic, Skills Match, Experience Relevance, and Education Alignment.

---

## Update 13: Persistent File Logging

**File:** `backend/api/main.py`

**Problem:** Logs only printed to the terminal. Once the server was stopped, all logs were lost — no persistent history for debugging or auditing.

**Fix:** Added dual logging — both terminal and file:
- Logs written to `backend/logs/app.log`
- Uses `RotatingFileHandler`: rotates at 5MB, keeps last 5 backup files
- Format: `2026-03-31 14:30:00,123 | INFO | cvmatch.requests | POST /api/v1/match | 200 | 3456ms | 127.0.0.1`
- `logs/` directory auto-created on startup
- `.gitkeep` preserves the directory in git, `*.log` already in `.gitignore`

---

## Update 14: Smart Experience Scoring

**Files:**
- `backend/services/similarity_engine.py`
- `backend/routes/match.py`

**Problem:** A "Store Associate" applying for a "Retail Store Associate" role only got ~47% on experience because pure embedding similarity doesn't recognize direct role matches.

**Fix:** Added `_experience_score()` method with job title comparison:
- Exact or substring title match (e.g., "Store Associate" in "Retail Store Associate") → score boosted to at least 85%
- 50%+ word overlap between titles → boosted to at least 75%
- 25%+ word overlap → boosted to at least 60%
- No match → falls back to semantic similarity
- CV job titles extracted from parsed experience data, JD title from first key phrase

---

## Update 15: Frontend Shows Actual Calculated Scores

**File:** `backend/services/matching_service.py`

**Problem:** Frontend displayed raw embedding similarities (e.g., Education Alignment 31.86%) but the actual score used in calculation was 80% (after the smart education boost). This mismatch confused users.

**Fix:** `section_similarities` in the API response now reads from the `breakdown` dict (which contains the boosted scores) instead of raw embedding values. What users see now matches what's actually being scored.

---

## Update 16: File Size Validation

**Files:**
- `frontend/app/page.tsx`
- `backend/routes/match.py`

**Problem:** Frontend displayed "up to 5MB" but nothing enforced the limit.

**Fix:**
- **Frontend:** Validates file size on upload, shows error if > 5MB
- **Backend:** Checks file size before processing, returns HTTP 413 if exceeded

---

## Update 17: OpenAI Rate Limit Handling

**Files:**
- `backend/services/openai_retry.py` (new)
- `backend/embedding/openai_encoder.py`
- `backend/cv_processor/parsers/openai_parser.py`
- `backend/nlp_preprocessing/cv_normalizer.py`
- `backend/nlp_preprocessing/job_preprocessor.py`
- `backend/services/similarity_engine.py`

**Problem:** All OpenAI API calls had no retry logic. If a rate limit or transient error occurred, the request simply failed.

**Fix:** Created `retry_openai_call()` utility with:
- Up to 3 retries with exponential backoff (1s, 2s, 4s)
- Handles `RateLimitError`, `APITimeoutError`, `APIConnectionError`
- Logs warnings on retry, errors on final failure
- Applied to all 5 modules that make OpenAI calls

---

## Update 18: CORS Configuration

**File:** `backend/api/main.py`

**Problem:** CORS was set to `"*"` (allow all origins). Fine for development but a security risk in production.

**Fix:**
- Default CORS origin is now `http://localhost:3000` (the frontend dev server)
- Configurable via `ALLOWED_ORIGINS` environment variable (comma-separated)
- Methods restricted to `GET` and `POST` only

---

## Update 19: Updated Tests

**File:** `backend/tests/test_similarity_engine.py`

**Changes:**
- Updated Jaccard test to verify JD-denominator scoring (3/5 not 3/7)
- Added test that extra CV skills don't penalize the score
- Updated calibration tests for new sigmoid parameters
- Added `TestEducationScoring` class (8 tests): exceeds/meets/below requirement, fallbacks, keyword parsing
- Added `TestExperienceScoring` class (6 tests): exact/substring/partial/no match, fallbacks
- Updated breakdown test to verify TF-IDF is NOT in breakdown
- **55 tests total, all passing**

---

## Known Remaining Issues

1. **Vector cache must be cleared** after prompt changes — delete `backend/vectors.db` when restarting after updates.
