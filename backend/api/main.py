from fastapi import FastAPI
from routes import cv, job_description, match

app = FastAPI(title="CVMatch API")

app.include_router(cv.router)
app.include_router(job_description.router)
app.include_router(match.router)