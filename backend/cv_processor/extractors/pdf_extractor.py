import pdfplumber
from typing import Optional, Union
from pathlib import Path
import io

class PDFExtractor:
    """Extract text from PDF files."""

    @staticmethod
    def extract(file_input: Union[str, Path, io.BytesIO]) -> Optional[str]:
        try:
            if isinstance(file_input, (str, Path)):
                pdf_file = file_input
            else:
                pdf_file = file_input

            text = []
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)

            return "\n".join(text) if text else None
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return None