"""Work experience extraction from CV text."""

import re
from typing import List, Dict, Optional
from datetime import datetime


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
            # Split into individual jobs (usually separated by company name or date)
            jobs = re.split(r'\n\s*(?=\d{1,2}[-/]|\w+\s+\d{4}|[A-Z])', experience_section)
            
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

    @staticmethod
    def _find_section(text: str, keywords: List[str]) -> Optional[str]:
        """Find a section by keywords."""
        text_lower = text.lower()
        section_pattern = '|'.join(keywords)
        match = re.search(rf'\b({section_pattern})\s*:?', text_lower)
        
        if match:
            start = match.end()
            # Find next section header
            next_section = re.search(r'\n\s*[A-Z][A-Za-z\s]+\s*:', text[start:])
            end = start + next_section.start() if next_section else len(text)
            return text[start:end]
        return None

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
        
        # Extract dates and titles
        for line in lines:
            dates = ExperienceParser._extract_dates(line)
            if dates:
                job["start_date"], job["end_date"] = dates
            
            if not job["title"] and len(line) < 80:
                job["title"] = line.strip()
            elif not job["company"] and len(line) < 80:
                job["company"] = line.strip()
            else:
                job["description"].append(line.strip())
        
        return job if (job["title"] or job["company"]) else None

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
        
        for line in lines:
            # Look for degree type
            if any(degree in line.lower() for degree in ['bachelor', 'master', 'phd', 'diploma', 'certificate']):
                education["degree"] = line.strip()
            
            # Look for GPA
            gpa_match = re.search(r'(?:gpa|cgpa)\s*:?\s*([\d.]+)', line.lower())
            if gpa_match:
                education["gpa"] = gpa_match.group(1)
            
            # Look for dates
            dates = ExperienceParser._extract_dates(line)
            if dates:
                education["graduation_date"] = dates[1] or dates[0]
            
            if not education["institution"]:
                education["institution"] = line.strip()
        
        return education if education["degree"] or education["institution"] else None

    @staticmethod
    def _extract_dates(text: str) -> Optional[tuple]:
        """Extract start and end dates from text."""
        dates = []
        for pattern in ExperienceParser.DATE_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                return (matches[0] if len(matches) > 0 else None,
                       matches[1] if len(matches) > 1 else None)
        return None
