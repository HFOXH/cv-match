"""Work experience extraction from CV text."""
import re
import spacy
from typing import List, Dict, Optional

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Model not found, try: python -m spacy download en_core_web_sm")
    nlp = None


class ExperienceParser:
    """Parse work experience and education from CV text."""

    MONTHS = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
        'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
    ]

    # Known section headings used to find section boundaries.
    SECTION_HEADINGS = [
        'experience', 'work experience', 'professional experience', 'work history',
        'education', 'academic', 'certifications', 'certificates',
        'skills', 'technical skills', 'core competencies',
        'projects', 'publications', 'references', 'languages',
        'summary', 'professional summary', 'objective', 'profile',
        'professional profile', 'achievements', 'awards', 'interests',
        'volunteer', 'additional information',
    ]

    # ------------------------------------------------------------------ #
    #  PUBLIC METHODS                                                       #
    # ------------------------------------------------------------------ #

    @staticmethod
    def extract_experience(text: str) -> List[Dict]:
        """Extract work experience entries from CV text."""
        experiences = []
        section = ExperienceParser._find_section(
            text, ['experience', 'work history', 'professional experience']
        )
        if not section or not nlp:
            return experiences

        lines = [l.strip() for l in section.split('\n') if l.strip()]

        blocks: List[List[str]] = []
        current_block: List[str] = []

        for line in lines:
            is_bullet = line[:1] in ('●', '•', '-', '○', '‣', '➤', '➔')
            has_year  = bool(re.search(r'\b(19|20)\d{2}\b', line))

            if has_year and not is_bullet:
                if current_block and not re.search(r'\b(19|20)\d{2}\b', current_block[-1]):
                    title_line = current_block.pop()
                    if current_block:
                        blocks.append(current_block)
                    current_block = [title_line, line]
                else:
                    if current_block:
                        blocks.append(current_block)
                    current_block = [line]
            else:
                current_block.append(line)

        if current_block:
            blocks.append(current_block)

        for block in blocks:
            job = ExperienceParser._parse_job_block(block)
            if job:
                experiences.append(job)

        return experiences

    @staticmethod
    def extract_education(text: str) -> List[Dict]:
        """Extract education entries from CV text."""
        education = []
        section = ExperienceParser._find_section(text, ['education', 'academic', 'degree'])
        if not section or not nlp:
            return education

        lines = [l.strip() for l in section.split('\n') if l.strip()]

        blocks: List[List[str]] = []
        current_block: List[str] = []

        DEGREE_KEYWORDS = [
            'bachelor', 'master', 'doctor', 'phd', 'engineer', 'degree',
            'licenciat', 'technolog', 'técnico', 'tecnólogo', 'ingeniería',
            'sistemas', 'analysis', 'analyst', 'diploma', 'certificate',
        ]

        for line in lines:
            lower = line.lower()
            is_degree_line = any(kw in lower for kw in DEGREE_KEYWORDS)

            if is_degree_line and current_block:
                blocks.append(current_block)
                current_block = [line]
            else:
                current_block.append(line)

        if current_block:
            blocks.append(current_block)

        for block in blocks:
            edu = ExperienceParser._parse_education_block(block)
            if edu:
                education.append(edu)

        return education

    # ------------------------------------------------------------------ #
    #  PRIVATE HELPERS                                                     #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_job_block(lines: List[str]) -> Optional[Dict]:
        """
        Turn a list of lines (one job block) into a job dict.

        Expected rough structure:
            line 0  → Job Title          (no year, no bullet)
            line 1  → Company | Date     (has year)
            line 2+ → bullet descriptions
        """
        if not lines:
            return None

        job: Dict = {
            "title": None,
            "company": None,
            "start_date": None,
            "end_date": None,
            "description": [],
        }

        for line in lines:
            is_bullet = line[:1] in ('●', '•', '-', '○', '‣', '➤', '➔')
            has_year  = bool(re.search(r'\b(19|20)\d{2}\b', line))

            if is_bullet:
                cleaned = line.lstrip('●•-○‣➤➔ ').strip()
                if cleaned:
                    job["description"].append(cleaned)
                continue

            if has_year:
                dates = ExperienceParser._extract_dates(line)
                if dates:
                    job["start_date"], job["end_date"] = dates

                doc = nlp(line)
                orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                if orgs:
                    job["company"] = orgs[0]
                elif '|' in line:
                    job["company"] = line.split('|')[0].strip()
                else:
                    remainder = ExperienceParser._strip_dates(line)
                    if remainder:
                        job["company"] = remainder
                continue

            if not job["title"]:
                job["title"] = line
            elif not job["company"]:
                job["company"] = line

        return job if (job["title"] or job["company"]) else None

    @staticmethod
    def _parse_education_block(lines: List[str]) -> Optional[Dict]:
        """Turn a list of lines (one education block) into an edu dict."""
        if not lines or not nlp:
            return None

        edu: Dict = {"degree": None, "institution": None, "graduation_date": None}

        for line in lines:
            has_year = bool(re.search(r'\b(19|20)\d{2}\b', line))
            line_doc = nlp(line)

            if has_year:
                dates = ExperienceParser._extract_dates(line)
                if dates:
                    edu["graduation_date"] = dates[1] or dates[0]
                orgs = [ent.text for ent in line_doc.ents if ent.label_ == "ORG"]
                if orgs and not edu["institution"]:
                    edu["institution"] = orgs[0]
                continue

            orgs = [ent.text for ent in line_doc.ents if ent.label_ == "ORG"]
            if orgs and not edu["institution"]:
                edu["institution"] = line
                continue

            DEGREE_KEYWORDS = [
                'bachelor', 'master', 'doctor', 'phd', 'engineer', 'degree',
                'licenciat', 'technolog', 'técnico', 'tecnólogo', 'ingeniería',
                'sistemas', 'analysis', 'analyst', 'diploma', 'certificate',
            ]
            if any(kw in line.lower() for kw in DEGREE_KEYWORDS) and not edu["degree"]:
                edu["degree"] = line
                continue

            if not edu["degree"]:
                edu["degree"] = line
            elif not edu["institution"]:
                edu["institution"] = line

        return edu if (edu["degree"] or edu["institution"]) else None

    @staticmethod
    def _find_section(text: str, keywords: List[str]) -> Optional[str]:
        """Find and return the text of a CV section by its heading keywords."""
        text_lower = text.lower()
        section_pattern = '|'.join(re.escape(kw) for kw in keywords)

        match = re.search(
            rf'^\s*({section_pattern})\s*:?\s*$',
            text_lower,
            re.MULTILINE,
        )
        if not match:
            match = re.search(rf'\b({section_pattern})\b\s*:?', text_lower)
        if not match:
            return None

        start = match.end()
        remaining = text[start:]

        heading_alt = '|'.join(
            re.escape(h) for h in ExperienceParser.SECTION_HEADINGS
            if h not in keywords
        )
        heading_match = re.search(
            rf'\n\s*(?:{heading_alt})\s*:?',
            remaining,
            re.IGNORECASE,
        )
        caps_match = re.search(r'\n\s*[A-Z][A-Z\s]{3,}$', remaining, re.MULTILINE)

        positions = []
        if heading_match:
            positions.append(heading_match.start())
        if caps_match:
            positions.append(caps_match.start())

        end = start + min(positions) if positions else len(text)
        return text[start:end]

    @staticmethod
    def _extract_dates(text: str) -> Optional[tuple]:
        """Extract start/end dates from a line of text using spaCy + regex fallback."""
        if not nlp:
            return None

        doc = nlp(text)
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]

        if not dates:
            year_matches = re.findall(r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+)?\d{4}\b', text, re.IGNORECASE)
            dates = [m.strip() for m in year_matches if m.strip()]

        if not dates:
            return None

        start_date = dates[0] if dates else None
        end_date   = dates[1] if len(dates) > 1 else None

        if not end_date:
            present = re.search(r'\b(present|current|now|actualidad|actual)\b', text, re.IGNORECASE)
            if present:
                end_date = present.group(1).capitalize()

        return (start_date, end_date) if start_date else None

    @staticmethod
    def _strip_dates(text: str) -> Optional[str]:
        """Remove date entities and separators from a line, returning leftover text."""
        if not nlp:
            return text

        doc = nlp(text)
        result = text
        for ent in doc.ents:
            if ent.label_ == "DATE":
                result = result.replace(ent.text, "")

        result = re.sub(r'\b(present|current|now|actualidad)\b', '', result, flags=re.IGNORECASE)
        result = re.sub(r'\s*[-\u2013\u2014|]+\s*', ' ', result)
        result = re.sub(r'\b(19|20)\d{2}\b', '', result)
        return result.strip(' ,;') or None