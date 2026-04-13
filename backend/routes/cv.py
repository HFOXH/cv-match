import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

# services must be imported before cv_processor.exceptions to keep the package
# init order stable (services.__init__ pulls in cv_processor transitively)
from services import CVService, normalization_service
from cv_processor.exceptions import ParsingError, ProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()

SERVICE_UNAVAILABLE_MESSAGE = (
    "Analysis service is temporarily unavailable. Please try again in a moment."
)


@router.post("/api/v1/cv/upload")
def upload_cv(file: UploadFile = File(...)):
    try:
        cv_result = CVService.process_cv(file)
        normalized_cv = normalization_service.normalize(cv_result["parsed_data"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ParsingError as e:
        logger.error("CV parsing failed: %s", e)
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)
    except Exception:
        logger.exception("Unexpected CV upload error")
        raise HTTPException(status_code=503, detail=SERVICE_UNAVAILABLE_MESSAGE)

    return {
        "cv_id": cv_result["cv_id"],
        "summary": cv_result["parsed_data"].get("summary"),
        "normalized_skills": normalized_cv.get("skills"),
        "embedding_text": normalized_cv.get("full_text_for_embedding"),
    }