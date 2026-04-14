import logging
import time

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

# services must be imported before cv_processor.exceptions to keep the package
# init order stable (services.__init__ pulls in cv_processor transitively)
from services import CVService, job_description_service, normalization_service, matching_service
from cv_processor.exceptions import ParsingError, ProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

SERVICE_UNAVAILABLE_MESSAGE = (
    "Analysis service is temporarily unavailable. Please try again in a moment."
)


@router.post("/api/v1/match")
def match_cv_with_jd(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB.")

    start_total = time.perf_counter()

    # Step 1: Process CV (extract + parse)
    try:
        t0 = time.perf_counter()
        cv_result = CVService.process_cv(file)
        cv_processing_ms = (time.perf_counter() - t0) * 1000
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ParsingError as e:
        logger.error("CV parsing failed: %s", e)
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)
    except Exception as e:
        logger.exception("Unexpected CV processing error")
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)

    # Step 2: Normalize CV data
    try:
        t0 = time.perf_counter()
        normalized_cv = normalization_service.normalize(cv_result["parsed_data"])
        cv_normalization_ms = (time.perf_counter() - t0) * 1000
    except Exception as e:
        logger.exception("CV normalization failed")
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)

    # Step 3: Preprocess job description
    try:
        t0 = time.perf_counter()
        jd_result = job_description_service.process(job_description)
        jd_preprocessing_ms = (time.perf_counter() - t0) * 1000
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("JD preprocessing failed")
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)

    # Step 4: Encode both using HybridEncoder (via MatchingService)
    try:
        t0 = time.perf_counter()
        cv_vectors = matching_service.encode_cv(
            cv_id=cv_result["cv_id"],
            normalized_cv=normalized_cv,
            raw_text=cv_result.get("raw_text", ""),
        )
        cv_encoding_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        jd_vectors = matching_service.encode_jd(jd_result)
        jd_encoding_ms = (time.perf_counter() - t0) * 1000
    except Exception as e:
        logger.exception("Embedding failed")
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)

    # If embeddings silently returned None (no API key, quota etc.), bail out —
    # we refuse to produce a misleading score from zero signal.
    if cv_vectors["section_embeddings"].get("overall") is None:
        logger.error("CV overall embedding unavailable — refusing to score")
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)
    if jd_vectors["section_embeddings"].get("overall") is None:
        logger.error("JD overall embedding unavailable — refusing to score")
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)

    # Pass education levels for smart comparison
    cv_vectors["education_level"] = cv_result["parsed_data"].get("education_level")
    jd_vectors["education_level"] = jd_result.get("education_level")

    # Pass job titles for experience matching
    cv_experience = cv_result["parsed_data"].get("experience", [])
    cv_vectors["job_titles"] = [
        e.get("job_title", "") for e in cv_experience
        if isinstance(e, dict) and e.get("job_title")
    ]
    jd_phrases = jd_result.get("key_phrases", [])
    jd_vectors["job_title"] = jd_phrases[0] if jd_phrases else None

    # Step 5: Compute match
    try:
        t0 = time.perf_counter()
        match_result = matching_service.compute_match(cv_vectors, jd_vectors)
        scoring_ms = (time.perf_counter() - t0) * 1000
    except Exception as e:
        logger.exception("Scoring failed")
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)

    total_ms = (time.perf_counter() - start_total) * 1000

    cv_summary = (
        cv_result["parsed_data"].get("summary")
        or normalized_cv.get("full_text_for_embedding")
        or None
    )

    return {
        "cv_id": cv_result["cv_id"],
        "match_score": match_result["match_score"],
        "overall_similarity": match_result["overall_similarity"],
        "section_similarities": match_result["section_similarities"],
        "cv_summary": cv_summary,
        "normalized_skills": normalized_cv.get("skills"),
        "required_skills": jd_result.get("required_skills"),
        "preferred_skills": jd_result.get("preferred_skills"),
        "experience_years": jd_result.get("experience_years"),
        "education_level": jd_result.get("education_level"),
        "key_phrases": jd_result.get("key_phrases"),
        "job_summary": jd_result.get("summary"),
        "match_percentage": match_result["match_percentage"],
        "match_rating": match_result["match_rating"],
        "recommendation": match_result["recommendation"],
        "confidence": match_result["confidence"],
        "breakdown": match_result["breakdown"],
        "raw_scores": match_result.get("raw_scores", {}),
        "skill_details": match_result.get("skill_details"),
        "strengths": match_result.get("strengths", []),
        "gaps": match_result.get("gaps", []),
        "timing": {
            "cv_processing_ms": round(cv_processing_ms),
            "cv_normalization_ms": round(cv_normalization_ms),
            "jd_preprocessing_ms": round(jd_preprocessing_ms),
            "cv_encoding_ms": round(cv_encoding_ms),
            "jd_encoding_ms": round(jd_encoding_ms),
            "scoring_ms": round(scoring_ms),
            "total_ms": round(total_ms),
        },
    }
