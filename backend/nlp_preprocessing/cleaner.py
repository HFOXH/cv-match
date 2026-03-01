import re
import logging

logger = logging.getLogger(__name__)

# --- Constants ---
K_URL_PATTERN = r'https?://\S+|www\.\S+'
K_EMAIL_PATTERN = r'\S+@\S+\.\S+'
K_NON_ASCII_PATTERN = r'[^\x00-\x7F]+'
K_MULTI_WHITESPACE_PATTERN = r'\s+'


class TextCleaner:
    """Stateless text cleaning utilities for preprocessing raw text."""

    # /*
    # * function name: clean_text()
    # * Description: Full cleaning pipeline for raw text. Removes URLs,
    # *              emails, non-ASCII characters, and normalizes whitespace.
    # * Parameter: text : str : Raw input text.
    # * return: str : Cleaned text string.
    # */
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""

        cleaned = re.sub(K_URL_PATTERN, '', text)
        cleaned = re.sub(K_EMAIL_PATTERN, '', cleaned)
        cleaned = re.sub(K_NON_ASCII_PATTERN, ' ', cleaned)
        cleaned = re.sub(K_MULTI_WHITESPACE_PATTERN, ' ', cleaned)
        cleaned = cleaned.strip()

        logger.debug("Cleaned text from %d to %d characters", len(text), len(cleaned))
        return cleaned

    # /*
    # * function name: remove_urls()
    # * Description: Remove all URLs from text.
    # * Parameter: text : str : Input text.
    # * return: str : Text with URLs removed.
    # */
    @staticmethod
    def remove_urls(text: str) -> str:
        return re.sub(K_URL_PATTERN, '', text)

    # /*
    # * function name: remove_emails()
    # * Description: Remove all email addresses from text.
    # * Parameter: text : str : Input text.
    # * return: str : Text with emails removed.
    # */
    @staticmethod
    def remove_emails(text: str) -> str:
        return re.sub(K_EMAIL_PATTERN, '', text)

    # /*
    # * function name: normalize_whitespace()
    # * Description: Collapse all runs of whitespace into single spaces.
    # * Parameter: text : str : Input text.
    # * return: str : Text with normalized whitespace.
    # */
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        return re.sub(K_MULTI_WHITESPACE_PATTERN, ' ', text).strip()

    # /*
    # * function name: normalize_skills()
    # * Description: Normalize a list of skill strings for consistent matching.
    # *              Lowercases, strips whitespace, removes blanks, deduplicates
    # *              while preserving order.
    # * Parameter: skills : list : List of skill name strings.
    # * return: list : Normalized, deduplicated skill list.
    # */
    @staticmethod
    def normalize_skills(skills: list) -> list:
        seen = set()
        normalized = []
        for skill in skills:
            s = skill.strip().lower()
            if s and s not in seen:
                seen.add(s)
                normalized.append(s)
        return normalized
