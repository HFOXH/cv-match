from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import cv, job_description, match

app = FastAPI(title="CVMatch API")

origins = [ "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv.router)
app.include_router(job_description.router)
app.include_router(match.router)