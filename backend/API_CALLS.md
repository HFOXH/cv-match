# OpenAI API Calls Reference

This document lists all external API calls (OpenAI) used by the CVMatch backend.

---

## 1. CV Parsing
- **File:** `cv_processor/parsers/openai_parser.py` (~95)  
- **Model:** gpt-4o-mini  
- **API Type:** chat.completions.create  
- **Purpose:** Parse CV text into structured sections (skills, experience, education, summary)  
- **When Called:** Every CV upload, unless the OpenAI API key is missing (fallback)

---

## 2. CV Normalization
- **File:** `nlp_preprocessing/cv_normalizer.py` (~89)  
- **Model:** gpt-4o-mini  
- **API Type:** chat.completions.create  
- **Purpose:** Normalize and standardize CV data (clean formatting, deduplicate skills)  
- **When Called:** After CV parsing succeeds

---

## 3. Job Description Preprocessing
- **File:** `nlp_preprocessing/job_preprocessor.py` (~152)  
- **Model:** gpt-4o-mini  
- **API Type:** chat.completions.create  
- **Purpose:** Extract required/preferred skills, years of experience, education level, key phrases from the job description text  
- **When Called:** Every match request

---

## 4. Single Embedding Generation
- **File:** `embedding/openai_encoder.py` (~51)  
- **Model:** text-embedding-3-small  
- **API Type:** embeddings.create  
- **Purpose:** Generate a single embedding vector for one text input  
- **When Called:** During CV/JD encoding (can be cached via vectors.db)

---

## 5. Batch Embedding Generation
- **File:** `embedding/openai_encoder.py` (~82)  
- **Model:** text-embedding-3-small  
- **API Type:** embeddings.create  
- **Purpose:** Generate embeddings for multiple sections (skills, experience, education, overall)  
- **When Called:** During CV/JD encoding (can be cached for CVs)

---

## 6. Semantic Skill Matching
- **File:** `services/similarity_engine.py` (~263)  
- **Model:** gpt-4o-mini  
- **API Type:** chat.completions.create  
- **Purpose:** Determine if unmatched CV skills are equivalent to JD skills (e.g., "React" = "React.js")  
- **When Called:** Only when unmatched skills exist after Jaccard matching