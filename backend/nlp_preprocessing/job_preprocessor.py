import json
import os
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from .cleaner import TextCleaner
from services.openai_retry import retry_openai_call
from prompts import K_EXTRACTION_SYSTEM_PROMPT, K_EXTRACTION_USER_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)


class JobDescriptionPreprocessor:
    """Hybrid preprocessing pipeline for job descriptions.

    - Traditional NLP: text cleaning
    - OpenAI API: skills extraction, classification, key phrase extraction
    """

    # /*
    # * function name: __init__()
    # * Description: Initialize the hybrid JD preprocessor. Sets up OpenAI client.
    # * Parameter: openai_api_key : Optional[str] : OpenAI API key. If None,
    # *              reads from OPENAI_API_KEY env var.
    # * return: None
    # */
    def __init__(self, openai_api_key: Optional[str] = None):

        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            logger.error("No OpenAI API key provided. JD extraction will not work.")

        logger.info("JobDescriptionPreprocessor initialized")

    # /*
    # * function name: preprocess()
    # * Description: Run the full hybrid preprocessing pipeline on a job description.
    # *              Traditional NLP handles text cleaning.
    # *              OpenAI handles skills extraction and classification.
    # * Parameter: text : str : Raw job description text.
    # * return: dict : Processed JD data with cleaned text, skills, and features.
    # */
    def preprocess(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            raise ValueError("Job description is empty")

        # Traditional NLP (mechanical processing)
        cleaned = self.clean_text(text)

        # OpenAI API (intelligent extraction) — raises on failure
        openai_extracted = self.openai_extract(cleaned)

        return {
            "original_text": text,
            "cleaned_text": cleaned,
            "key_phrases": openai_extracted.get("key_phrases", []),
            "required_skills": TextCleaner.normalize_skills(openai_extracted.get("required_skills", [])),
            "preferred_skills": TextCleaner.normalize_skills(openai_extracted.get("preferred_skills", [])),
            "experience_years": openai_extracted.get("experience_years"),
            "education_level": openai_extracted.get("education_level"),
            "experience_requirements": openai_extracted.get("experience_requirements"),
            "education_requirements": openai_extracted.get("education_requirements"),
            "summary": openai_extracted.get("summary"),
        }

    # /*
    # * function name: clean_text()
    # * Description: Clean raw job description text using TextCleaner.
    # * Parameter: text : str : Raw input text.
    # * return: str : Cleaned text.
    # */
    def clean_text(self, text: str) -> str:
        return TextCleaner.clean_text(text)

    # /*
    # * function name: openai_extract()
    # * Description: Use OpenAI GPT-4o-mini to extract structured information
    # *              from a job description in a single API call. Returns empty
    # *              result and logs error if the API call fails.
    # * Parameter: text : str : Cleaned job description text.
    # * return: dict : Extracted data with skills, classification, key phrases.
    # */
    def openai_extract(self, text: str) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("OpenAI client not available for JD extraction")

        prompt = K_EXTRACTION_USER_PROMPT.format(jd_text=text)

        response = retry_openai_call(
            self.client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": K_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=1200,
        )

        result = response.choices[0].message.content.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        return json.loads(result)

    # --- Private helpers ---

