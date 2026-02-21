"""Main CV Processor module that orchestrates all extraction and parsing."""

import os
from typing import Dict, Optional, Any

from ..extractors.pdf_extractor import PDFExtractor
from ..extractors.docx_extractor import DOCXExtractor
from ..extractors.txt_extractor import TXTExtractor

from ..parsers.contact_parser import ContactParser
from ..parsers.skills_parser import SkillsParser
from ..parsers.experience_parser import ExperienceParser

from ..normalizers.normalizer import Normalizer


class CVProcessor:
    """Main class for processing CVs and extracting structured information."""

    SUPPORTED_FORMATS = {
        '.pdf': PDFExtractor,
        '.docx': DOCXExtractor,
        '.doc': DOCXExtractor,
        '.txt': TXTExtractor,
    }

    @staticmethod
    def process_file(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a CV file and extract structured information.
        
        Args:
            file_path: Path to the CV file
            
        Returns:
            Dictionary with extracted information or None if processing fails
        """
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        _, file_ext = os.path.splitext(file_path)
        file_ext = file_ext.lower()
        
        # Check if format is supported
        if file_ext not in CVProcessor.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Extract raw text
        extractor_class = CVProcessor.SUPPORTED_FORMATS[file_ext]
        raw_text = extractor_class.extract(file_path)
        
        if not raw_text:
            raise ValueError("Failed to extract text from file")
        
        # Process and structure the text
        return CVProcessor.process_text(raw_text)

    @staticmethod
    def process_text(text: str) -> Dict[str, Any]:
        """
        Process raw CV text and extract structured information.
        
        Args:
            text: Raw CV text
            
        Returns:
            Dictionary with structured CV information
        """
        if not text:
            raise ValueError("Empty text provided")
        
        # Extract from raw text first (preserves structure)
        contact_info = ContactParser.extract(text)
        skills = SkillsParser.extract(text)
        experience = ExperienceParser.extract_experience(text)
        education = ExperienceParser.extract_education(text)
        
        # Normalize text for storage
        normalized_text = Normalizer.normalize_text(text)
        
        # Build result
        result = {
            "raw_text": text,
            "normalized_text": normalized_text,
            "contact": contact_info,
            "skills": Normalizer.standardize_skills(skills) if skills else [],
            "experience": experience,
            "education": education,
        }
        
        return result

    @staticmethod
    def process_directory(directory_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Process all CV files in a directory.
        
        Args:
            directory_path: Path to directory containing CV files
            
        Returns:
            Dictionary mapping filenames to processed CV data
        """
        results = {}
        
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Check if file is a supported format
            _, ext = os.path.splitext(filename)
            if ext.lower() not in CVProcessor.SUPPORTED_FORMATS:
                continue
            
            try:
                results[filename] = CVProcessor.process_file(file_path)
            except Exception as e:
                results[filename] = {"error": str(e)}
        
        return results
