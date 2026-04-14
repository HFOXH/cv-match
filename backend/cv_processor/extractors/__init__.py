"""Text extraction modules for PDF, DOCX, and TXT files.

Authors: Santiago Cardenas and Amel Sunil
First version: 2025-02-27
"""

from .pdf_extractor import PDFExtractor
from .docx_extractor import DOCXExtractor
from .txt_extractor import TXTExtractor

__all__ = ["PDFExtractor", "DOCXExtractor", "TXTExtractor"]
