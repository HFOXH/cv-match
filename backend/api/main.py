import io
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from cv_processor import CVProcessor
from cv_processor.exceptions import ProcessingError
from cv_processor.extractors.docx_extractor import DOCXExtractor
from cv_processor.extractors.pdf_extractor import PDFExtractor
from cv_processor.extractors.txt_extractor import TXTExtractor

app = FastAPI(title="CVMatch API")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt"
}

EXTRACTOR_MAP = {
    "pdf": PDFExtractor,
    "docx": DOCXExtractor,
    "txt": TXTExtractor
}

@app.post("/api/v1/cv/upload")
async def upload_cv(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: PDF, DOCX, TXT")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 5MB limit")

    cv_id = str(uuid.uuid4())
    extension = ALLOWED_TYPES[file.content_type]

    try:
        if extension == "txt":
            text = contents.decode("utf-8", errors="ignore").strip()
        else:
            extractor_class = EXTRACTOR_MAP[extension]
            file_like = io.BytesIO(contents)
            text = extractor_class.extract(file_like)

        if not text or not text.strip():
            raise ProcessingError("Unable to extract text from the CV")

        result = CVProcessor.process_text(text, file_type=extension)

        return JSONResponse(
            status_code=200,
            content={
                "cv_id": cv_id,
                "status": "processed",
                "parsing_method": result.get("parsing_method"),
                "summary": result.get("parsed_data", {}).get("summary")
            }
        )

    except ProcessingError:
        raise HTTPException(status_code=500, detail="CV processing failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")