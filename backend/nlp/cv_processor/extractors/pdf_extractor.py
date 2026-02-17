"""PDF text extraction module."""

import pdfplumber
from typing import Optional


class PDFExtractor:
    """Extract text from PDF files."""

    @staticmethod
    def extract(file_path: str) -> Optional[str]:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            text = []
            with pdfplumber.open(file_path) as pdf:
                # Handle password-protected files
                if pdf.is_encrypted:
                    return None
                    
                # Extract text from all pages
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            
            return "\n".join(text) if text else None
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return None
