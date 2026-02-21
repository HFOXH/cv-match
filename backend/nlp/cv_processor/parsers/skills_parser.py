"""Skills extraction from CV text using spaCy PhraseMatcher."""

import re
import warnings
from typing import List, Set, Optional

from .skills_database import SKILLS_DATABASE

try:
    import spacy
    from spacy.matcher import PhraseMatcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class SkillsParser:
    """Parse skills from CV text using spaCy PhraseMatcher."""

    # Class-level singleton state for lazy loading
    _nlp = None
    _matcher: Optional[object] = None
    _initialized: bool = False
    _use_spacy: bool = False

    # Skills that are too short/ambiguous for document-wide matching.
    # These are only accepted when found inside an explicit skills section.
    SHORT_SKILLS = {'c', 'r'}

    # Imported from skills_database.py — organized by category there.
    SKILLS_DATABASE = SKILLS_DATABASE

    # Section-detection keywords (regex patterns)
    # The colon is optional — many resumes use "SKILLS" as a standalone heading.
    SKILLS_KEYWORDS = [
        r'technical\s+skills?\s*:?',
        r'core\s+competencies?\s*:?',
        r'skills?\s*:?',
        r'competencies?\s*:?',
    ]

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Lazy-load spaCy model and build PhraseMatcher patterns."""
        if cls._initialized:
            return

        if not SPACY_AVAILABLE:
            warnings.warn("spaCy not installed. Falling back to regex matching.")
            cls._use_spacy = False
            cls._initialized = True
            return

        try:
            cls._nlp = spacy.load(
                "en_core_web_sm",
                disable=["ner", "parser", "lemmatizer"],
            )
            cls._matcher = PhraseMatcher(cls._nlp.vocab, attr="LOWER")
            patterns = [cls._nlp.make_doc(variant) for variant in cls.SKILLS_DATABASE]
            cls._matcher.add("SKILLS", patterns)
            cls._use_spacy = True
        except OSError:
            warnings.warn(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm. "
                "Falling back to regex matching."
            )
            cls._use_spacy = False

        cls._initialized = True

    @staticmethod
    def extract(text: str) -> List[str]:
        """
        Extract skills from text.

        Args:
            text: Raw CV text

        Returns:
            List of standardized skills
        """
        SkillsParser._ensure_initialized()

        skills: Set[str] = set()
        text_lower = text.lower()

        # Stage 1: Document-wide matching
        if SkillsParser._use_spacy:
            skills.update(SkillsParser._match_with_spacy(text))
        else:
            skills.update(SkillsParser._match_with_regex(text_lower))

        # Stage 2: Section-aware extraction (complement)
        # Pass original text so section boundary regex can detect uppercase headings
        skills_section = SkillsParser._find_skills_section(text)
        if skills_section:
            skills.update(SkillsParser._extract_from_section(skills_section))

        return list(skills)

    @staticmethod
    def _match_with_spacy(text: str) -> Set[str]:
        """Match skills using spaCy PhraseMatcher across full document."""
        skills: Set[str] = set()
        doc = SkillsParser._nlp(text)
        matches = SkillsParser._matcher(doc)

        for match_id, start, end in matches:
            span_text = doc[start:end].text.lower()
            # Skip short/ambiguous skills in document-wide scan
            if span_text in SkillsParser.SHORT_SKILLS:
                continue
            canonical = SkillsParser.SKILLS_DATABASE.get(span_text)
            if canonical:
                skills.add(canonical)

        return skills

    @staticmethod
    def _match_with_regex(text_lower: str) -> Set[str]:
        """Fallback: match skills using regex when spaCy is unavailable."""
        skills: Set[str] = set()
        for skill, canonical in SkillsParser.SKILLS_DATABASE.items():
            if skill in SkillsParser.SHORT_SKILLS:
                continue
            pattern = r'(?:^|\W)' + re.escape(skill) + r'(?:\W|$)'
            if re.search(pattern, text_lower, re.IGNORECASE):
                skills.add(canonical)
        return skills

    # Common section headings used to detect where the skills section ends.
    SECTION_HEADINGS = [
        'experience', 'work experience', 'professional experience', 'work history',
        'education', 'academic', 'certifications', 'certificates',
        'projects', 'publications', 'references', 'languages',
        'summary', 'professional summary', 'objective', 'profile',
        'professional profile', 'achievements', 'awards', 'interests',
        'volunteer', 'additional information',
    ]

    @staticmethod
    def _find_skills_section(text: str) -> str:
        """Find the skills section in the text.

        Receives the original (not lowercased) text so that section-boundary
        detection works correctly with uppercase headings.
        """
        text_lower = text.lower()

        # Find the start of the skills section
        for keyword_pattern in SkillsParser.SKILLS_KEYWORDS:
            match = re.search(keyword_pattern, text_lower)
            if match:
                start = match.end()

                # Find the next section heading after the skills section.
                # Two separate searches: known headings (case-insensitive)
                # and ALL-CAPS lines (case-sensitive).
                remaining = text[start:]
                heading_alt = '|'.join(
                    re.escape(h) for h in SkillsParser.SECTION_HEADINGS
                )
                heading_match = re.search(
                    rf'\n\s*(?:{heading_alt})\s*:?',
                    remaining,
                    re.IGNORECASE,
                )
                caps_match = re.search(
                    r'\n\s*[A-Z][A-Z\s]{3,}$',
                    remaining,
                    re.MULTILINE,
                )
                positions = []
                if heading_match:
                    positions.append(heading_match.start())
                if caps_match:
                    positions.append(caps_match.start())
                end = start + min(positions) if positions else len(text)
                return text[start:end]
        return ""

    @staticmethod
    def _extract_from_section(section: str) -> List[str]:
        """Extract skills from a skills section."""
        skills = []
        # Split by common delimiters including various bullet characters
        # U+2022 (•), U+25CF (●), U+25CB (○), U+2023 (‣), U+27A4 (➤)
        items = re.split(r'[,;•●○‣➤➔|\n]', section)

        for item in items:
            # Strip whitespace and any remaining bullet/dash prefixes
            item = item.strip().lstrip('-– ')
            if item and len(item) < 50:
                canonical = SkillsParser.SKILLS_DATABASE.get(
                    item.lower(),
                    item.title() if len(item) > 1 else None,
                )
                if canonical:
                    skills.append(canonical)

        return skills
