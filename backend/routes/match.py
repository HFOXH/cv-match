from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.cv_service import CVService
from services.job_description_service import JDService
from services.normalization_service import NormalizationService
from services.matching_service import MatchingService

router = APIRouter()

job_description_service = JDService()
normalization_service = NormalizationService()
matching_service = MatchingService()


@router.post("/api/v1/match")
async def match_cv_with_jd(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    try:
        # Step 1: Process CV (extract + parse)
        cv_result = CVService.process_cv(file)
        parsing_method = cv_result.get("parsing_method", "openai")

        # Step 2: Normalize CV data
        normalized_cv = normalization_service.normalize(cv_result["parsed_data"])

        # Step 3: Preprocess job description
        jd_result = job_description_service.process(job_description)

        # Step 4: Encode both using HybridEncoder (via MatchingService)
        cv_vectors = matching_service.encode_cv(
            cv_id=cv_result["cv_id"],
            normalized_cv=normalized_cv,
            raw_text=cv_result.get("raw_text", ""),
            parsing_method=parsing_method,
        )

        jd_vectors = matching_service.encode_jd(jd_result)

        # Step 5: Compute match
        match_result = matching_service.compute_match(cv_vectors, jd_vectors)

        return {
            "cv_id": cv_result["cv_id"],
            "match_score": match_result["match_score"],
            "overall_similarity": match_result["overall_similarity"],
            "section_similarities": match_result["section_similarities"],
            "tfidf_similarity": match_result["tfidf_similarity"],
            "cv_summary": cv_result["parsed_data"].get("summary"),
            "normalized_skills": normalized_cv.get("skills"),
            "required_skills": jd_result.get("required_skills"),
            "preferred_skills": jd_result.get("preferred_skills"),
            "experience_years": jd_result.get("experience_years"),
            "education_level": jd_result.get("education_level"),
            "key_phrases": jd_result.get("key_phrases"),
            "job_summary": jd_result.get("summary"),
            "is_fallback": match_result["_fallback"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
