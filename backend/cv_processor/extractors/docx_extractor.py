# /*
# FILE : docx_extractor.py
# PROJECT : CVMatch - CV Processing Module (Task 1)
# PROGRAMMER : Santiago Cardenas and Amel Sunil
# FIRST VERSION : 2025-02-27
# DESCRIPTION : Extracts raw text from DOCX (Word) files using python-docx.
#               Handles both paragraphs and table content.
# */

from docx import Document
from typing import Optional


class DOCXExtractor:
    """Extract text from DOCX (Word) files."""

    # /*
    # * function name: extract()
    # * Description: Extract text from a DOCX file. Reads all paragraphs first,
    # *              then extracts text from any tables in the document.
    # * Parameter: file_path : str : Path to the DOCX file.
    # * return: Optional[str] : Extracted text or None if extraction fails.
    # */
    @staticmethod
    def extract(file_path: str) -> Optional[str]:
        try:
            doc = Document(file_path)
            text = []

            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)

            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text)
                    if row_text:
                        text.append(" | ".join(row_text))

            return "\n".join(text) if text else None
        except Exception as e:
            print(f"Error extracting DOCX text: {str(e)}")
            return None
