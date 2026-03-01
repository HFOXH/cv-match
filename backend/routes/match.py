from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import numpy as np

from services.cv_service import CVService
from services.job_description_service import JDService
from services.normalization_service import NormalizationService
from openai import OpenAI

router = APIRouter()

job_description_service = JDService()
normalization_service = NormalizationService()

openai_client = OpenAI(api_key=None)

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))) * 100  # porcentaje

@router.post("/api/v1/match")
async def match_cv_with_jd(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        cv_result = CVService.process_cv(file)
        normalized_cv = normalization_service.normalize(cv_result["parsed_data"])

        jd_result = job_description_service.process(job_description)

        cv_text = normalized_cv.get("full_text_for_embedding", "")
        jd_text = jd_result.get("cleaned_text", "")

        cv_embedding_resp = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=cv_text
        )
        jd_embedding_resp = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=jd_text
        )

        cv_embedding = cv_embedding_resp.data[0].embedding
        jd_embedding = jd_embedding_resp.data[0].embedding

        score = cosine_similarity(cv_embedding, jd_embedding)

        return {
            "cv_id": cv_result["cv_id"],
            "match_score": round(score, 2),
            "cv_summary": cv_result["parsed_data"].get("summary"),
            "normalized_skills": normalized_cv.get("skills"),
            "required_skills": jd_result.get("required_skills"),
            "preferred_skills": jd_result.get("preferred_skills"),
            "experience_years": jd_result.get("experience_years"),
            "education_level": jd_result.get("education_level"),
            "key_phrases": jd_result.get("key_phrases"),
            "job_summary": jd_result.get("summary"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))