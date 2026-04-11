import json
import os
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from .cleaner import TextCleaner
from services.openai_retry import retry_openai_call

load_dotenv()

logger = logging.getLogger(__name__)

K_EXTRACTION_SYSTEM_PROMPT = (
    "You are a precise job description parser. Return only valid JSON, no markdown."
)

K_EXTRACTION_USER_PROMPT = """Analyze this job description and extract structured information.
Return ONLY valid JSON with these fields:

{{
    "required_skills": ["skills explicitly marked as required/must-have"],
    "preferred_skills": ["skills marked as preferred/nice-to-have/bonus"],
    "experience_years": "experience requirement as string (e.g., '3-5 years') or null",
    "education_level": "highest education mentioned (PhD/Master's/Bachelor's) or null",
    "experience_requirements": "Factual summary of experience needed: years of experience, types of roles, domains, and key responsibilities. Use neutral language. Examples: '1-2 years of retail or customer service experience preferred.' or '3+ years of full stack development experience.' If none found, use null.",
    "education_requirements": "Factual summary of education needed: degree levels, fields of study, certifications. Use neutral language. Examples: 'High school diploma or equivalent.' or 'Bachelor's degree in Computer Science or related field.' If none found, use null.",
    "key_phrases": ["important multi-word phrases that capture the role essence, e.g., 'retail store associate', 'customer service', 'food safety compliance', 'project management'"],
    "summary": "Concise summary of the job description, max 250 words"
}}

Rules:
- Normalize skill names from ANY industry (e.g., 'JS' -> 'JavaScript', 'POS' -> 'point of sale', 'CPR' -> 'CPR certification')
- If a skill is not clearly required or preferred, put it in required_skills
- Include both hard skills (tools, certifications, technical abilities) and soft skills (communication, leadership, teamwork, multitasking)
- This applies to ALL industries: retail, healthcare, trades, hospitality, IT, education, manufacturing, etc.
- Do NOT include physical requirements as skills (e.g., "ability to stand for extended periods", "ability to lift 50 lbs", "ability to work in cold environments", "physical stamina"). These are working conditions, not skills.
- Do NOT include generic availability requirements as skills (e.g., "flexible schedule", "available weekends")
- Key phrases should be bigrams/trigrams that capture the role essence
- Summary should be clear, professional, and no more than 250 words

Job Description:
{jd_text}"""


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
            logger.warning("Empty text provided to preprocess")
            return self._empty_result(text or "")

        # Traditional NLP (mechanical processing)
        cleaned = self.clean_text(text)

        # OpenAI API (intelligent extraction)
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
            logger.error("OpenAI client not available. Cannot extract JD features.")
            return self._empty_extraction()

        prompt = K_EXTRACTION_USER_PROMPT.format(jd_text=text)

        try:
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

        except json.JSONDecodeError as e:
            logger.error("Failed to parse OpenAI response as JSON: %s", e)
            return self._empty_extraction()
        except Exception as e:
            logger.error("OpenAI API call failed: %s", e)
            return self._empty_extraction()

    # --- Private helpers ---

    @staticmethod
    def _empty_extraction() -> Dict[str, Any]:
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": None,
            "education_level": None,
            "experience_requirements": None,
            "education_requirements": None,
            "key_phrases": [],
            "summary": None,
        }

    @staticmethod
    def _empty_result(text: str) -> Dict[str, Any]:
        return {
            "original_text": text,
            "cleaned_text": "",
            "key_phrases": [],
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": None,
            "education_level": None,
            "experience_requirements": None,
            "education_requirements": None,
            "summary": None,
        }
