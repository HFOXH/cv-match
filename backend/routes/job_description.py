from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from services import job_description_service

router = APIRouter()


class JDRequest(BaseModel):
    text: str


@router.post("/api/v1/jd/preprocess")
def preprocess_job_description(body: JDRequest):

    try:
        result = job_description_service.process(body.text)

        return {
            "cleaned_text": result.get("cleaned_text"),
            "required_skills": result.get("required_skills"),
            "preferred_skills": result.get("preferred_skills"),
            "experience_years": result.get("experience_years"),
            "education_level": result.get("education_level"),
            "key_phrases": result.get("key_phrases"),
            "summary": result.get("summary")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))