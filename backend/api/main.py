import logging
import os
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import cv, job_description, match
from middleware.request_logger import RequestLoggingMiddleware

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Log format with timestamp
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# File handler — rotates at 5MB, keeps last 5 files
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configure root logger
logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])

app = FastAPI(title="CVMatch API")
app.add_middleware(RequestLoggingMiddleware)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(cv.router)
app.include_router(job_description.router)
app.include_router(match.router)