import os
from typing import Dict, Any

from .extractors.pdf_extractor import PDFExtractor
from .extractors.docx_extractor import DOCXExtractor
from .extractors.txt_extractor import TXTExtractor
from .parsers.openai_parser import get_parser
from .exceptions import ProcessingError, ParsingError

K_MIN_CV_TEXT_LENGTH = 50

class CVProcessor:
    """Orchestrates text extraction and structured CV parsing."""

    K_SUPPORTED_FORMATS = {
        '.pdf': PDFExtractor,
        '.docx': DOCXExtractor,
        '.doc': DOCXExtractor,
        '.txt': TXTExtractor,
    }

    @staticmethod
    def process_file(file_path: str) -> Dict[str, Any]:
        """
        Process a CV file: validate, extract text, parse structured data.

        Args:
            file_path: Path to the CV file (PDF, DOCX, TXT).

        Returns:
            Dict with raw_text, parsed_data, parsing_method, and metadata.

        Raises:
            FileNotFoundError, ValueError, ProcessingError
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        _, file_ext = os.path.splitext(file_path)
        file_ext = file_ext.lower()

        if file_ext not in CVProcessor.K_SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_ext}")

        extractor_class = CVProcessor.K_SUPPORTED_FORMATS[file_ext]
        raw_text = extractor_class.extract(file_path)

        if not raw_text or len(raw_text.strip()) < K_MIN_CV_TEXT_LENGTH:
            raise ProcessingError("CV text is too short or empty")

        return CVProcessor.process_text(raw_text, file_type=file_ext.lstrip('.'))

    @staticmethod
    def process_text(text: str, file_type: str = "text") -> Dict[str, Any]:
        """
        Parse raw CV text into structured data using OpenAI.

        Raises ParsingError if the OpenAI parser is unavailable or fails —
        callers should surface a service-unavailable response to the user.
        """
        if not text.strip():
            raise ProcessingError("Empty text provided")

        parser = get_parser()
        if not parser:
            raise ParsingError("OpenAI CV parser is not configured")

        parsed_data = parser.parse_cv(text)

        return {
            "raw_text": text,
            "parsed_data": parsed_data,
            "metadata": {
                "file_type": file_type,
                "text_length": len(text),
                "skills_count": len(parsed_data.get("skills", [])),
                "experience_count": len(parsed_data.get("experience", [])),
            },
        }

    @staticmethod
    def process_directory(directory_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Process all supported CV files in a directory.

        Args:
            directory_path: Path to directory containing CV files.

        Returns:
            Dict mapping filenames to processed CV data or error messages.
        """
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")

        results = {}
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            if os.path.isdir(file_path):
                continue

            _, ext = os.path.splitext(filename)
            if ext.lower() not in CVProcessor.K_SUPPORTED_FORMATS:
                continue

            try:
                results[filename] = CVProcessor.process_file(file_path)
            except Exception as e:
                results[filename] = {"error": str(e)}

        return results