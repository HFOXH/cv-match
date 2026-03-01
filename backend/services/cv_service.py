import io
import uuid

from cv_processor import CVProcessor
from cv_processor.exceptions import ProcessingError
from cv_processor.extractors.docx_extractor import DOCXExtractor
from cv_processor.extractors.pdf_extractor import PDFExtractor
from cv_processor.extractors.txt_extractor import TXTExtractor

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

class CVService:

    @staticmethod
    def process_cv(file):
        if file.content_type not in ALLOWED_TYPES:
            raise ValueError("Unsupported file type")

        contents = file.file.read()

        extension = ALLOWED_TYPES[file.content_type]

        if extension == "txt":
            text = contents.decode("utf-8", errors="ignore").strip()
        else:
            extractor_class = EXTRACTOR_MAP[extension]
            file_like = io.BytesIO(contents)
            text = extractor_class.extract(file_like)

        if not text or not text.strip():
            raise ProcessingError("Unable to extract text")

        result = CVProcessor.process_text(text, file_type=extension)

        return {
            "cv_id": str(uuid.uuid4()),
            "raw_text": text,
            "parsed_data": result.get("parsed_data", {}),
            "parsing_method": result.get("parsing_method")
        }