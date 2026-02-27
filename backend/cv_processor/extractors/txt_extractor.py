# /*
# FILE : txt_extractor.py
# PROJECT : CVMatch - CV Processing Module (Task 1)
# PROGRAMMER : Santiago Cardenas and Amel Sunil
# FIRST VERSION : 2025-02-27
# DESCRIPTION : Extracts raw text from plain text files with automatic
#               encoding detection using chardet.
# */

from typing import Optional
import chardet


class TXTExtractor:
    """Extract text from plain text files."""

    # /*
    # * function name: extract()
    # * Description: Extract text from a TXT file. Detects the file encoding
    # *              automatically using chardet, then reads the content.
    # * Parameter: file_path : str : Path to the TXT file.
    # * return: Optional[str] : Extracted text or None if extraction fails.
    # */
    @staticmethod
    def extract(file_path: str) -> Optional[str]:
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')

            # Read with detected encoding
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                text = f.read().strip()

            return text if text else None
        except Exception as e:
            print(f"Error extracting TXT text: {str(e)}")
            return None
