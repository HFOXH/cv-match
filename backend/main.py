from fastapi import FastAPI
from pydantic import BaseModel
from nlp.matcher import compute_match

app = FastAPI()

class MatchRequest(BaseModel):
    cv_text: str
    job_text: str

@app.post("/match")
def match_cv(request: MatchRequest):
    score = compute_match(request.cv_text, request.job_text)
    return {"match_percentage": score}
