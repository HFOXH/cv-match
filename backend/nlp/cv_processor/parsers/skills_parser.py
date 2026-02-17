"""Skills extraction from CV text."""

import re
from typing import List


class SkillsParser:
    """Parse skills from CV text."""

    # Common skills and their standardized names
    SKILLS_MAPPING = {
        'js': 'JavaScript',
        'ts': 'TypeScript',
        'python': 'Python',
        'java': 'Java',
        'cpp': 'C++',
        'c#': 'C#',
        'sql': 'SQL',
        'postgresql': 'PostgreSQL',
        'mysql': 'MySQL',
        'mongodb': 'MongoDB',
        'react': 'React',
        'angular': 'Angular',
        'vue': 'Vue.js',
        'node': 'Node.js',
        'nodejs': 'Node.js',
        'fastapi': 'FastAPI',
        'django': 'Django',
        'flask': 'Flask',
        'aws': 'AWS',
        'gcp': 'Google Cloud',
        'azure': 'Azure',
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'git': 'Git',
        'ml': 'Machine Learning',
        'ai': 'Artificial Intelligence',
        'dl': 'Deep Learning',
        'nlp': 'NLP',
        'machine learning': 'Machine Learning',
        'deep learning': 'Deep Learning',
        'tensorflow': 'TensorFlow',
        'pytorch': 'PyTorch',
        'scikit-learn': 'Scikit-learn',
        'html': 'HTML',
        'css': 'CSS',
        'restapi': 'REST API',
        'graphql': 'GraphQL',
    }

    SKILLS_KEYWORDS = [
        r'skills?\s*:',
        r'competencies?\s*:',
        r'technical\s+skills?\s*:',
        r'core\s+competencies?\s*:',
    ]

    @staticmethod
    def extract(text: str) -> List[str]:
        """
        Extract skills from text.
        
        Args:
            text: Raw CV text
            
        Returns:
            List of standardized skills
        """
        skills = []
        text_lower = text.lower()

        # Try to find skills section
        skills_section = SkillsParser._find_skills_section(text_lower)
        
        if skills_section:
            # Extract from skills section
            skills.extend(SkillsParser._extract_from_section(skills_section))
        
        # Also search for skills throughout document
        for skill, standardized in SkillsParser.SKILLS_MAPPING.items():
            # Use word boundary or punctuation/space as boundaries
            pattern = r'(?:^|\W)' + re.escape(skill) + r'(?:\W|$)'
            if re.search(pattern, text_lower, re.IGNORECASE):
                if standardized not in skills:
                    skills.append(standardized)
        
        return list(set(skills))  # Remove duplicates

    @staticmethod
    def _find_skills_section(text: str) -> str:
        """Find the skills section in the text."""
        for keyword_pattern in SkillsParser.SKILLS_KEYWORDS:
            match = re.search(keyword_pattern, text)
            if match:
                # Extract text after the keyword until next section
                start = match.end()
                next_section = re.search(r'\n\s*[A-Z][A-Za-z\s]+\s*:', text[start:])
                end = start + next_section.start() if next_section else len(text)
                return text[start:end]
        return ""

    @staticmethod
    def _extract_from_section(section: str) -> List[str]:
        """Extract skills from a skills section."""
        skills = []
        # Split by common delimiters
        items = re.split(r'[,;•\n]', section)
        
        for item in items:
            item = item.strip()
            if item and len(item) < 50:  # Skip very long items
                standardized = SkillsParser.SKILLS_MAPPING.get(
                    item.lower(), 
                    item.title()
                )
                if standardized:
                    skills.append(standardized)
        
        return skills
