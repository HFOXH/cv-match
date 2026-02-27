# /*
# FILE : pdf_extractor.py
# PROJECT : CVMatch - CV Processing Module (Task 1)
# PROGRAMMER : Santiago Cardenas and Amel Sunil
# FIRST VERSION : 2025-02-27
# DESCRIPTION : Extracts raw text from PDF files using pdfplumber.
#               Handles multi-page resumes and returns combined text.
# */

import pdfplumber
from typing import Optional


class PDFExtractor:
    """Extract text from PDF files."""

    # /*
    # * function name: extract()
    # * Description: Extract text from a PDF file page by page using pdfplumber.
    # *              Joins all page texts with newlines.
    # * Parameter: file_path : str : Path to the PDF file.
    # * return: Optional[str] : Extracted text or None if extraction fails.
    # */
    @staticmethod
    def extract(file_path: str) -> Optional[str]:
        try:
            text = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)

            return "\n".join(text) if text else None
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return None
