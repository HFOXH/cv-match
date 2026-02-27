# /*
# FILE : __init__.py
# PROJECT : CVMatch - CV Processing Module (Task 1)
# PROGRAMMER : Santiago Cardenas and Amel Sunil
# FIRST VERSION : 2025-02-27
# DESCRIPTION : Text extraction modules for PDF, DOCX, and TXT files.
# */

from .pdf_extractor import PDFExtractor
from .docx_extractor import DOCXExtractor
from .txt_extractor import TXTExtractor

__all__ = ["PDFExtractor", "DOCXExtractor", "TXTExtractor"]
