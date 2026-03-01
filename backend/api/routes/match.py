from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.cv_service import CVService
from services.job_description_service import JDService
from services.normalization_service import NormalizationService
from services.matching_service import MatchingService

router = APIRouter()

job_description_service = JDService()
normalization_service = NormalizationService()


@router.post("/api/v1/match")
async def match_cv_with_jd(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):

    try:
        cv_result = CVService.process_cv(file)

        normalized_cv = normalization_service.normalize(cv_result["parsed_data"])

        jd_result = job_description_service.process(job_description)

        # 4️⃣ Embeddings (cuando los conectes)
        # cv_embedding = embed(normalized_cv["full_text_for_embedding"])
        # jd_embedding = embed(jd_result["cleaned_text"])

        # score = MatchingService.compute_match(cv_embedding, jd_embedding)

        score = 87.5  # temporal

        return {
            "cv_id": cv_result["cv_id"],
            "match_score": score,
            "cv_summary": cv_result["parsed_data"].get("summary"),
            "normalized_skills": normalized_cv.get("skills"),
            "required_skills": jd_result.get("required_skills"),
            "preferred_skills": jd_result.get("preferred_skills")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))