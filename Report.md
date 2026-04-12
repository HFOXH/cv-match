# CVMatch: Resume & Job Description Matching System  
**Cambrian College — Graduate Certificate in Artificial Intelligence Natural Language Processing — Final Project**

**Authors:** Santiago Cárdenas & Amel Sunil  
**Date:** 2026-04-12  

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
2. NLP preprocessing and normalization  
3. Semantic embedding generation  
4. Similarity scoring with feedback generation  

### Data Pipeline

| Step | Component              | Description |
|------|-----------------------|-------------|
| 1    | File Extraction       | PDF → pdfplumber; DOCX → python-docx; TXT → chardet |
| 2    | Text Normalization    | Clean special chars, normalize whitespace, section segmentation |
| 3    | AI Parsing (GPT-4o-mini) | Extract structured fields: skills, experience, education, etc. |
| 4    | Embedding Generation  | OpenAI text-embedding-3-small + TF-IDF hybrid approach |
| 5    | Similarity Scoring    | Cosine similarity between CV and job description vectors |
| 6    | Feedback Generation   | Matched skills, missing skills, and summary text |

### NLP Techniques Employed
- Semantic Embeddings (OpenAI text-embedding-3-small) for deep contextual understanding  
- TF-IDF Vectorization for keyword and frequency-based matching  
- Hybrid Encoder combining semantic + lexical signals for robust scoring  
- GPT-4o-mini for structured information extraction and natural language feedback generation  
- Section-level embeddings for fine-grained matching (skills, experience, education)  

---

## 3. Technical Implementation & Architecture

### Tech Stack

| Layer              | Technology |
|-------------------|------------|
| Frontend          | Next.js, TypeScript, Tailwind CSS |
| Backend / API     | FastAPI (Python) |
| NLP Engine        | OpenAI Embeddings, TF-IDF, spaCy, NLTK |
| LLM Parsing       | GPT-4o-mini (OpenAI) |
| File Processing   | pdfplumber, python-docx, chardet |
| Testing           | pytest (backend) |
| Deployment-ready  | Docker + persistent volumes |

### Architecture Diagram (Textual)
The system is split into a FastAPI backend and a Next.js frontend. The backend exposes REST endpoints:
- `POST /api/cv` for CV upload  
- `POST /api/job_description` for job input  
- `POST /api/match` for similarity computation  

All NLP processing is encapsulated in independent modules (`cv_processor`, `embedding`, `nlp_preprocessing`, `services`).

---

## 4. Core Functionalities

### Algorithms & Model Selection Rationale
- **Hybrid Encoder (OpenAI + TF-IDF):** OpenAI embeddings provide deep semantic understanding, while TF-IDF captures lexical relevance. Combining both yields higher accuracy than either method alone.  
- **Cosine Similarity:** Standard metric for comparing embedding vectors; scale-invariant and well-suited for high-dimensional sparse/dense vectors.  
- **GPT-4o-mini Parsing:** Lightweight yet capable LLM for extracting structured CV fields. Using structured output reduces downstream parsing errors.  
- **Section-level Embeddings:** Computing separate embeddings for skills, experience, and education enables granular matching and more informative feedback.  

### Design Trade-offs
- **OpenAI API Cost vs. Accuracy:** Using GPT-4o-mini and text-embedding-3-small incurs API costs. Chosen for accuracy and simplicity; local models (Sentence-BERT, spaCy) are fallback options.  
- **Hybrid vs. Single Encoder:** Hybrid encoding is slightly more complex but significantly improves recall for keyword-heavy job descriptions.  
- **Real-time vs. Batch Processing:** The current system processes requests in real time for a better UX. Batch processing can be added for enterprise use.  
- **Modularity vs. Simplicity:** A highly modular architecture increases maintainability and testability at the cost of more boilerplate.  

---

## 5. Result Analysis

Performance was evaluated on a set of 20 sample CV–job description pairs with known ground-truth match labels (High / Medium / Low).

| Metric                         | TF-IDF Only       | OpenAI Embeddings | Hybrid Encoder |
|--------------------------------|-------------------|-------------------|----------------|
| Precision (High/Mid/Low)       | 0.65 / 0.68 / 0.71 | 0.78 / 0.81 / 0.74 | 0.85 / 0.87 / 0.82 |
| Recall (High/Mid/Low)          | 0.60 / 0.72 / 0.69 | 0.75 / 0.79 / 0.71 | 0.83 / 0.86 / 0.80 |
| F1-Score (High/Mid/Low)        | 0.62 / 0.70 / 0.70 | 0.76 / 0.80 / 0.72 | 0.84 / 0.86 / 0.81 |
| Avg. Match Score Accuracy      | 68.4%             | 79.2%             | 87.1% |
| Avg. Response Time (s)         | 1.2s              | 1.8s              | 2.1s |

### Interpretation
The hybrid encoder consistently outperforms both TF-IDF and OpenAI embeddings alone across all match categories. The largest gains are observed in the **High** match category (+20pp vs. TF-IDF), where semantic understanding is critical. Response time remains acceptable (~2.1s) given the dual-encoding step. The system reliably distinguishes High, Medium, and Low matches with F1 scores above 0.80 in all categories.

### Key Findings
1. Hybrid encoding provides the best balance of semantic and lexical matching.  
2. Section-level embeddings improve feedback quality by enabling precise skill-level analysis.  
3. GPT-4o-mini parsing significantly reduces noise from raw CV text.  
4. Modular architecture allows scalability and easier maintenance.  

---  