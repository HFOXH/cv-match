# normalizer.py
"""Text normalization and skill standardization for CV parsing."""

import re
import unicodedata
from dateparser import parse as parse_date
from skills_database import SKILLS_DATABASE

class Normalizer:
    """Normalize and standardize text, skills, and dates."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Basic normalization: remove extra spaces and normalize unicode."""
        if not text:
            return ""
        text = ' '.join(text.split())
        text = unicodedata.normalize('NFKD', text)
        return text

    @staticmethod
    def clean_text(text: str, preserve_structure: bool = False) -> str:
        """Remove unwanted characters, optionally preserve sentence structure."""
        if not text:
            return ""
        if preserve_structure:
            text = re.sub(r'[^\w\s.,:;()\-/]', '', text)
        else:
            text = re.sub(r'[^\w\s]', '', text)
        return ' '.join(text.split())

    @staticmethod
    def lowercase_except_acronyms(text: str) -> str:
        """Lowercase text but preserve acronyms (2+ capital letters)."""
        if not text:
            return ""
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        text = text.lower()
        for acronym in acronyms:
            text = text.replace(acronym.lower(), acronym)
        return text

    @staticmethod
    def standardize_skills(skills: list) -> list:
        """Map input skills to canonical names using the skills database."""
        standardized = set()
        for skill in skills:
            key = skill.strip().lower()
            canonical = SKILLS_DATABASE.get(key, skill.strip().title())
            standardized.add(canonical)
        return list(standardized)

    @staticmethod
    def handle_date_formats(date_str: str) -> str:
        """Parse and standardize dates to YYYY-MM-DD."""
        if not date_str:
            return ""
        dt = parse_date(date_str)
        return dt.strftime("%Y-%m-%d") if dt else date_str

    @staticmethod
    def full_normalization(text: str) -> str:
        """Run full text normalization pipeline."""
        text = Normalizer.normalize_text(text)
        text = Normalizer.clean_text(text)
        text = Normalizer.lowercase_except_acronyms(text)
        return text