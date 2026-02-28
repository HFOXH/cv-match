from typing import Optional
import chardet

class TXTExtractor:
    """Extract text from plain text files using automatic encoding detection."""

    @staticmethod
    def extract(file_path: str) -> Optional[str]:
        """
        Extract text from a TXT file.

        Detects encoding using chardet and returns the cleaned text.
        Returns None if extraction fails or file is empty.
        """
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data).get("encoding", "utf-8")

            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                text = f.read().strip()

            return text or None

        except Exception:
            return None