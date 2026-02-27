# /*
# FILE : processor.py
# PROJECT : CVMatch - CV Processing Module (Task 1)
# PROGRAMMER : Santiago Cardenas and Amel Sunil
# FIRST VERSION : 2025-02-27
# DESCRIPTION : Main CV Processor module that orchestrates the full pipeline.
#               Extracts raw text from CV files (PDF, DOCX, TXT) and sends
#               it to OpenAI GPT-4o-mini for structured parsing. Includes
#               fallback mode when the API is unavailable.
# */

import os
from typing import Dict, Any

from .extractors.pdf_extractor import PDFExtractor
from .extractors.docx_extractor import DOCXExtractor
from .extractors.txt_extractor import TXTExtractor
from .parsers.openai_parser import get_parser, fallback_parse
from .exceptions import ProcessingError, ParsingError

K_MIN_CV_TEXT_LENGTH = 50


class CVProcessor:
    """Orchestrates text extraction and OpenAI parsing."""

    K_SUPPORTED_FORMATS = {
        '.pdf': PDFExtractor,
        '.docx': DOCXExtractor,
        '.doc': DOCXExtractor,
        '.txt': TXTExtractor,
    }

    # /*
    # * function name: process_file()
    # * Description: Full CV processing pipeline. Validates the file, extracts
    # *              raw text using the appropriate extractor, then parses it
    # *              via OpenAI with fallback support.
    # * Parameter: file_path : str : Path to the CV file (PDF, DOCX, or TXT).
    # * return: dict : Dictionary with raw_text, parsed_data, parsing_method,
    # *                and metadata.
    # */
    @staticmethod
    def process_file(file_path: str) -> Dict[str, Any]:
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

    # /*
    # * function name: process_text()
    # * Description: Parse raw CV text into structured data via OpenAI.
    # *              Falls back to minimal parsing if the API is unavailable
    # *              or returns an error.
    # * Parameter: text : str : Raw CV text.
    # *            file_type : str : Source file type (pdf, docx, txt, text).
    # * return: dict : Dictionary with raw_text, parsed_data, parsing_method,
    # *                and metadata including skill and experience counts.
    # */
    @staticmethod
    def process_text(text: str, file_type: str = "text") -> Dict[str, Any]:
        if not text or not text.strip():
            raise ProcessingError("Empty text provided")

        parser = get_parser()
        if parser is not None:
            try:
                parsed_data = parser.parse_cv(text)
                parsing_method = "openai"
            except ParsingError:
                parsed_data = fallback_parse(text)
                parsing_method = "fallback"
        else:
            parsed_data = fallback_parse(text)
            parsing_method = "fallback"

        return {
            "raw_text": text,
            "parsed_data": parsed_data,
            "parsing_method": parsing_method,
            "metadata": {
                "file_type": file_type,
                "text_length": len(text),
                "skills_count": len(parsed_data.get("skills", [])),
                "experience_count": len(parsed_data.get("experience", [])),
            },
        }

    # /*
    # * function name: process_directory()
    # * Description: Process all supported CV files in a given directory.
    # *              Returns a dictionary mapping each filename to its
    # *              processed result or an error message.
    # * Parameter: directory_path : str : Path to directory containing CV files.
    # * return: dict : Dictionary mapping filenames to processed CV data.
    # */
    @staticmethod
    def process_directory(directory_path: str) -> Dict[str, Dict[str, Any]]:
        results = {}

        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")

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
