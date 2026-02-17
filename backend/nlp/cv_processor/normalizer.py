"""Text normalization and standardization."""

import re
import unicodedata


class Normalizer:
    """Normalize and standardize text data."""

    # Common abbreviations to expand
    ABBREVIATIONS = {
        'js': 'javascript',
        'ts': 'typescript',
        'cpp': 'c++',
        'cs': 'c#',
        'ml': 'machine learning',
        'dl': 'deep learning',
        'ai': 'artificial intelligence',
        'nlp': 'natural language processing',
        'cv': 'computer vision',
        'db': 'database',
        'api': 'application programming interface',
        'rest': 'representational state transfer',
        'sql': 'structured query language',
        'nosql': 'nosql',
        'orm': 'object relational mapping',
        'crud': 'create read update delete',
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for consistency.
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        return text

    @staticmethod
    def clean_text(text: str, preserve_structure: bool = False) -> str:
        """
        Clean text by removing special characters while preserving important formatting.
        
        Args:
            text: Text to clean
            preserve_structure: Whether to preserve formatting
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        if preserve_structure:
            # Keep punctuation at end of sentences
            text = re.sub(r'[^\w\s.,:;()\-/]', '', text)
        else:
            # Remove most special characters
            text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    @staticmethod
    def lowercase_except_acronyms(text: str) -> str:
        """
        Convert text to lowercase while preserving acronyms.
        
        Args:
            text: Text to convert
            
        Returns:
            Text with selective lowercasing
        """
        if not text:
            return ""
        
        # Find all acronyms (consecutive capitals)
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Restore acronyms
        for acronym in acronyms:
            text = text.replace(acronym.lower(), acronym)
        
        return text

    @staticmethod
    def expand_abbreviations(text: str) -> str:
        """
        Expand common abbreviations.
        
        Args:
            text: Text with abbreviations
            
        Returns:
            Text with expanded abbreviations
        """
        text_lower = text.lower()
        
        for abbr, expansion in Normalizer.ABBREVIATIONS.items():
            # Use word boundaries to match whole words
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text_lower = re.sub(pattern, expansion, text_lower)
        
        return text_lower

    @staticmethod
    def standardize_skills(skills: list) -> list:
        """
        Standardize skill names.
        
        Args:
            skills: List of skill names
            
        Returns:
            List of standardized skill names
        """
        standardized = []
        
        for skill in skills:
            skill = skill.strip().title()
            
            # Apply standardization mappings
            if skill.lower() == 'javascript':
                skill = 'JavaScript'
            elif skill.lower() == 'typescript':
                skill = 'TypeScript'
            elif skill.lower() == 'react':
                skill = 'React'
            elif skill.lower() == 'node':
                skill = 'Node.js'
            
            standardized.append(skill)
        
        return list(set(standardized))  # Remove duplicates

    @staticmethod
    def handle_date_formats(date_str: str) -> str:
        """
        Standardize date formats to YYYY-MM-DD.
        
        Args:
            date_str: Date in various formats
            
        Returns:
            Standardized date
        """
        if not date_str:
            return ""
        
        # Try to parse and standardize
        # This is a simplified version - a full implementation would use dateparser
        
        # Handle Month YYYY format
        month_pattern = r'([A-Za-z]+)\s+(\d{4})'
        match = re.search(month_pattern, date_str)
        if match:
            month_names = {
                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
            }
            month = month_names.get(match.group(1).lower()[:3])
            year = match.group(2)
            if month:
                return f"{year}-{month}-01"
        
        # Handle MM/DD/YYYY or DD/MM/YYYY format
        slash_pattern = r'(\d{1,2})/(\d{1,2})/(\d{4})'
        match = re.search(slash_pattern, date_str)
        if match:
            # Assume MM/DD/YYYY for now
            return f"{match.group(3)}-{match.group(1).zfill(2)}-{match.group(2).zfill(2)}"
        
        return date_str
