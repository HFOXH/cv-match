import io
import logging
from pathlib import Path
from typing import Optional, Union

import pdfplumber

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text from PDF files."""

    # /*
    # * function name: extract()
    # * Description: Extract text from a PDF file page by page using pdfplumber.
    # * Parameter: file_input : Union[str, Path, io.BytesIO] : File path or
    # *              in-memory bytes buffer.
    # * return: Optional[str] : Extracted text or None if extraction fails.
    # */
    @staticmethod
    def extract(file_input: Union[str, Path, io.BytesIO]) -> Optional[str]:
        try:
            text = []
            with pdfplumber.open(file_input) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)

            return "\n".join(text) if text else None
        except Exception as e:
            logger.error("Error extracting PDF text: %s", e)
            return None
