"""TXT file extraction module."""

from typing import Optional
import chardet


class TXTExtractor:
    """Extract text from plain text files."""

    @staticmethod
    def extract(file_path: str) -> Optional[str]:
        """
        Extract text from a TXT file with encoding detection.
        
        Args:
            file_path: Path to the TXT file
            
        Returns:
            Extracted text or None if extraction fails
        """
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
