import logging
import os
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import cv, job_description, match
from middleware.request_logger import RequestLoggingMiddleware

# Log format with timestamp
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Console handler — always on. In containers, `docker logs` captures this.
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

handlers = [console_handler]

# Optional file handler for local dev. Set LOG_TO_FILE=1 to enable. In Docker,
# leave this unset so logs go only to stdout and don't fill the container FS.
if os.getenv("LOG_TO_FILE") == "1":
    LOG_DIR = os.getenv(
        "LOG_DIR",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"),
    )
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handlers.append(file_handler)

# Configure root logger
logging.basicConfig(level=logging.INFO, handlers=handlers)

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