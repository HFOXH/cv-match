import io
import logging
from pathlib import Path
from typing import Optional, Union

import pdfplumber

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Extract text from a PDF file.

    Parameters
    ----------
    file_input : Union[str, Path, io.BytesIO]
        Path to a PDF file, Path object, or a file-like bytes buffer.

    Returns
    -------
    Optional[str]
        The concatenated text from all pages of the PDF, or `None` if extraction fails.

    Notes
    -----
    - Logs errors via the `logging` module.
    - Extraction may be incomplete for PDFs with scanned images or unusual layouts.
    """
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
