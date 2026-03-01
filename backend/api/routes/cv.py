from fastapi import APIRouter, UploadFile, File, HTTPException
from services.cv_service import CVService
from services.normalization_service import NormalizationService

router = APIRouter()

normalization_service = NormalizationService()


@router.post("/api/v1/cv/upload")
async def upload_cv(file: UploadFile = File(...)):

    try:
        cv_result = CVService.process_cv(file)

        normalized_cv = normalization_service.normalize(
            cv_result["parsed_data"]
        )

        return {
            "cv_id": cv_result["cv_id"],
            "parsing_method": cv_result["parsing_method"],
            "summary": cv_result["parsed_data"].get("summary"),
            "normalized_skills": normalized_cv.get("skills"),
            "embedding_text": normalized_cv.get("full_text_for_embedding")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))