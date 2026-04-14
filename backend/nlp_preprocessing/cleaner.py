import re
import logging
import unicodedata

logger = logging.getLogger(__name__)

K_URL_PATTERN = r'https?://\S+|www\.\S+'
K_EMAIL_PATTERN = r'\S+@\S+\.\S+'
K_MULTI_WHITESPACE_PATTERN = r'\s+'


class TextCleaner:
    """Stateless text cleaning utilities for preprocessing raw text and normalizing skill lists."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing URLs, emails, non-ASCII characters, and normalizing whitespace."""
        if not text:
            return ""
        cleaned = re.sub(K_URL_PATTERN, '', text)
        cleaned = re.sub(K_EMAIL_PATTERN, '', cleaned)
        cleaned = unicodedata.normalize('NFKD', cleaned)
        cleaned = cleaned.encode('ascii', 'ignore').decode('ascii')
        cleaned = re.sub(K_MULTI_WHITESPACE_PATTERN, ' ', cleaned)
        return cleaned.strip()

    @staticmethod
    def normalize_skills(skills: list) -> list:
        """Normalize and deduplicate a list of skill strings.

        Defensive against None lists, None items, and non-string items
        (LLMs occasionally emit null entries or wrap skills in dicts).
        """
        seen = set()
        normalized = []
        for skill in skills or []:
            if not isinstance(skill, str):
                continue
            s = skill.strip().lower()
            if s and s not in seen:
                seen.add(s)
                normalized.append(s)
        return normalized

    @staticmethod
    def remove_urls(text: str) -> str:
        return re.sub(K_URL_PATTERN, '', text)

    @staticmethod
    def remove_emails(text: str) -> str:
        return re.sub(K_EMAIL_PATTERN, '', text)

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        return re.sub(K_MULTI_WHITESPACE_PATTERN, ' ', text).strip()
