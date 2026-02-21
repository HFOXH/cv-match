"""Contact information extraction using regex patterns and NLP."""

import re
from typing import Dict, Optional


class ContactParser:
    """Parse contact information from CV text."""

    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = (
        r'\(?\+?\d{1,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{0,4}'
        r'|\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}'
        r'|\+\d{1,3}[-.\s]\d[\d\s.-]{6,14}'
    )

    @staticmethod
    def extract(text: str) -> Dict[str, Optional[str]]:
        return {
            "name": ContactParser._extract_name(text),
            "emails": ContactParser._extract_email(text),
            "phone": ContactParser._extract_phone(text)
        }

    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """Extract name from first lines using capitalization heuristics."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:10]:
            if any(keyword in line.lower() for keyword in ['email', 'phone', 'address', 'linkedin', 'github']):
                continue
            # Heuristic: line has 2-4 words, each capitalized
            words = line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words):
                return line
        return None

    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        """Extract email address."""
        match = re.search(ContactParser.EMAIL_PATTERN, text)
        return match.group(0) if match else None

    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        """Extract phone number."""
        match = re.search(ContactParser.PHONE_PATTERN, text)
        return match.group(0) if match else None
