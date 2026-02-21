"""Work experience extraction from CV text."""

import re
from typing import List, Dict, Optional


class ExperienceParser:
    """Parse work experience and education from CV text."""

    DATE_PATTERNS = [
        r'(\w+\s+\d{4})',  # Month YYYY
        r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
        r'(\d{4}-\d{1,2}-\d{1,2})',  # YYYY-MM-DD
        r'(\d{1,2}\.\d{1,2}\.\d{4})',  # DD.MM.YYYY
    ]

    MONTHS = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december',
              'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

    @staticmethod
    def extract_experience(text: str) -> List[Dict]:
        """
        Extract work experience from text.
        
        Args:
            text: Raw CV text
            
        Returns:
            List of experience dictionaries
        """
        experiences = []
        
        # Look for experience section
        experience_section = ExperienceParser._find_section(text, ['experience', 'work history', 'professional experience'])
        
        if experience_section:
            # Split into individual jobs on lines that start with a date.
            # The bare [A-Z] alternative was removed — it split on every capitalised
            # line, fragmenting multi-line job descriptions.
            month_alt = '|'.join(ExperienceParser.MONTHS)
            jobs = re.split(
                rf'\n(?=\d{{1,2}}[-/]|\b(?:{month_alt})\s+\d{{4}})',
                experience_section,
                flags=re.IGNORECASE,
            )
            
            for job_text in jobs:
                if job_text.strip():
                    job = ExperienceParser._parse_job(job_text)
                    if job:
                        experiences.append(job)
        
        return experiences

    @staticmethod
    def extract_education(text: str) -> List[Dict]:
        """
        Extract education information from text.
        
        Args:
            text: Raw CV text
            
        Returns:
            List of education dictionaries
        """
        education = []
        
        # Look for education section
        edu_section = ExperienceParser._find_section(text, ['education', 'academic', 'degree'])
        
        if edu_section:
            # Split into individual degrees
            degrees = re.split(r'\n\s*(?=[A-Z][a-z]+\s+(?:of|in)|\d{4})', edu_section)
            
            for degree_text in degrees:
                if degree_text.strip():
                    degree = ExperienceParser._parse_education(degree_text)
                    if degree:
                        education.append(degree)
        
        return education

    # Common section headings for detecting section boundaries.
    SECTION_HEADINGS = [
        'experience', 'work experience', 'professional experience', 'work history',
        'education', 'academic', 'certifications', 'certificates',
        'skills', 'technical skills', 'core competencies',
        'projects', 'publications', 'references', 'languages',
        'summary', 'professional summary', 'objective', 'profile',
        'professional profile', 'achievements', 'awards', 'interests',
        'volunteer', 'additional information',
    ]

    @staticmethod
    def _find_section(text: str, keywords: List[str]) -> Optional[str]:
        """Find a section by keywords.

        Looks for keywords as section headings (at the start of a line),
        not as words within sentences.
        """
        text_lower = text.lower()

        # Build pattern that matches keywords at the start of a line
        # to avoid matching "experience" inside "Experienced in..."
        section_pattern = '|'.join(re.escape(kw) for kw in keywords)
        match = re.search(
            rf'^\s*({section_pattern})\s*:?\s*$',
            text_lower,
            re.MULTILINE,
        )

        # Fallback: match keyword preceded by a newline (for headings
        # that share a line with other text like "WORK EXPERIENCE")
        if not match:
            match = re.search(
                rf'\b({section_pattern})\b\s*:?',
                text_lower,
            )

        if not match:
            return None

        start = match.end()
        remaining = text[start:]

        # Find the next section heading after this section.
        # Two separate searches to avoid IGNORECASE breaking ALL-CAPS detection.

        # 1) Known headings (case-insensitive)
        heading_alt = '|'.join(
            re.escape(h) for h in ExperienceParser.SECTION_HEADINGS
            if h not in keywords  # don't match the same section
        )
        heading_match = re.search(
            rf'\n\s*(?:{heading_alt})\s*:?',
            remaining,
            re.IGNORECASE,
        )

        # 2) ALL-CAPS lines like "EDUCATION" (case-sensitive, no IGNORECASE)
        caps_match = re.search(
            r'\n\s*[A-Z][A-Z\s]{3,}$',
            remaining,
            re.MULTILINE,
        )

        # Take whichever boundary comes first
        positions = []
        if heading_match:
            positions.append(heading_match.start())
        if caps_match:
            positions.append(caps_match.start())

        end = start + min(positions) if positions else len(text)
        return text[start:end]

    @staticmethod
    def _parse_job(text: str) -> Optional[Dict]:
        """Parse individual job entry."""
        lines = text.strip().split('\n')
        if not lines:
            return None

        job = {
            "title": None,
            "company": None,
            "start_date": None,
            "end_date": None,
            "description": []
        }

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            dates = ExperienceParser._extract_dates(stripped)
            if dates:
                job["start_date"], job["end_date"] = dates

                # Extract company name from remainder of date line.
                # Format: "Oct 2023 - Present Symplifica"
                remainder = ExperienceParser._strip_dates(stripped)
                if remainder and not job["company"] and len(remainder) < 80:
                    job["company"] = remainder
                continue

            if not job["title"] and len(stripped) < 80:
                job["title"] = stripped
            elif not job["company"] and len(stripped) < 80:
                job["company"] = stripped
            else:
                # Strip bullet prefixes (•, ●, ○, ‣, ➤, -, –)
                cleaned = stripped.lstrip('•●○‣➤➔-– ').strip()
                if cleaned:
                    job["description"].append(cleaned)

        return job if (job["title"] or job["company"]) else None

    @staticmethod
    def _strip_dates(text: str) -> Optional[str]:
        """Remove date patterns and separators from a line, returning leftover text."""
        month_alt = '|'.join(ExperienceParser.MONTHS)
        # Remove month-year patterns
        result = re.sub(rf'(?:{month_alt})\s+\d{{4}}', '', text, flags=re.IGNORECASE)
        # Remove numeric date patterns
        result = re.sub(r'\d{1,2}[/.-]\d{1,2}[/.-]\d{4}', '', result)
        result = re.sub(r'\d{4}[-]\d{1,2}[-]\d{1,2}', '', result)
        # Remove "Present" / "Current" / "Now"
        result = re.sub(r'\b(?:present|current|now)\b', '', result, flags=re.IGNORECASE)
        # Remove separators (dashes, en-dashes, em-dashes)
        result = re.sub(r'\s*[-\u2013\u2014]+\s*', ' ', result)
        # Clean up
        result = result.strip(' ,;|')
        return result if result else None

    @staticmethod
    def _parse_education(text: str) -> Optional[Dict]:
        """Parse individual education entry."""
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        if not lines:
            return None

        education = {
            "degree": None,
            "institution": None,
            "graduation_date": None,
            "gpa": None
        }

        DEGREE_KEYWORDS = [
            'bachelor', 'master', 'phd', 'doctorate', 'diploma', 'certificate',
            'postgraduate', 'undergraduate', 'associate', 'engineering',
            'development', 'technology', 'science', 'arts', 'degree', 'systems',
        ]

        # Matches "2022 - 2023", "2025 – Present", "2020 — Current" (regular, en, em dash)
        YEAR_RANGE_RE = re.compile(
            r'\d{4}\s*[-\u2013\u2014]\s*(?:\d{4}|[Pp]resent|[Cc]urrent)'
        )

        for line in lines:
            # Look for GPA
            gpa_match = re.search(r'(?:gpa|cgpa)\s*:?\s*([\d.]+)', line.lower())
            if gpa_match:
                education["gpa"] = gpa_match.group(1)
                continue

            # Extract graduation date from year range first
            if not education["graduation_date"]:
                yr_match = YEAR_RANGE_RE.search(line)
                if yr_match:
                    education["graduation_date"] = yr_match.group(0)

            # Fall back to standard date patterns
            if not education["graduation_date"]:
                dates = ExperienceParser._extract_dates(line)
                if dates:
                    education["graduation_date"] = dates[1] or dates[0]

            # Strip year ranges from line before classifying degree / institution
            clean_line = YEAR_RANGE_RE.sub('', line).strip(' \t\u2013\u2014-').strip()

            if not clean_line:
                continue

            # Classify as degree, then institution (use elif to avoid double-assigning)
            if not education["degree"] and any(kw in clean_line.lower() for kw in DEGREE_KEYWORDS):
                education["degree"] = clean_line
            elif not education["institution"] and clean_line != education.get("degree"):
                education["institution"] = clean_line

        return education if education["degree"] or education["institution"] else None

    @staticmethod
    def _extract_dates(text: str) -> Optional[tuple]:
        """Extract start and end dates from text."""
        # Build a month-anchored pattern from the MONTHS list to avoid false positives
        # like "Engineer 2020" matching the generic \w+\s+\d{4} pattern.
        month_alt = '|'.join(ExperienceParser.MONTHS)
        patterns = [
            rf'((?:{month_alt})\s+\d{{4}})',  # Month YYYY (validated against known months)
            ExperienceParser.DATE_PATTERNS[1],  # MM/DD/YYYY
            ExperienceParser.DATE_PATTERNS[2],  # YYYY-MM-DD
            ExperienceParser.DATE_PATTERNS[3],  # DD.MM.YYYY
        ]

        start_date = None
        end_date = None

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                start_date = matches[0]
                end_date = matches[1] if len(matches) > 1 else None
                break

        # Capture "Present" / "Current" / "Now" as an end date for ongoing roles
        if start_date and not end_date:
            present_match = re.search(r'\b(present|current|now)\b', text, re.IGNORECASE)
            if present_match:
                end_date = present_match.group(1).capitalize()

        return (start_date, end_date) if start_date else None
