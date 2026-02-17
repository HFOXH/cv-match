"""Contact information extraction using regex patterns and NLP."""

import re
from typing import Dict, Optional


class ContactParser:
    """Parse contact information from CV text."""

    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+\d{1,15}'

    @staticmethod
    def extract(text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from text.
        
        Args:
            text: Raw CV text
            
        Returns:
            Dictionary with name, email, and phone
        """
        contact = {
            "name": ContactParser._extract_name(text),
            "email": ContactParser._extract_email(text),
            "phone": ContactParser._extract_phone(text)
        }
        return contact

    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """
        Extract name from text (typically at the beginning).
        
        Args:
            text: Raw CV text
            
        Returns:
            Name or None
        """
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 100:  # Names are usually short
                # Skip lines with common keywords
                if not any(keyword in line.lower() for keyword in 
                          ['email', 'phone', 'address', 'link', 'linkedin', 'github']):
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
