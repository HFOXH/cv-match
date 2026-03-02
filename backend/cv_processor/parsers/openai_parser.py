import json
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from ..exceptions import ParsingError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

K_SYSTEM_PROMPT = """You are a CV/resume parser. Extract structured information from the provided CV text.
Always respond with valid JSON matching the exact schema provided.
If a field cannot be determined from the text, use null for single values or empty arrays for lists.
Do not invent or hallucinate information — only extract what is explicitly present in the text."""

K_USER_PROMPT_TEMPLATE = """Parse the following CV/resume text and extract structured information.

IMPORTANT: For the "skills" field, extract ALL skills, technologies, tools, and frameworks from the ENTIRE CV — including the Skills/Technical Skills section, "Technologies used" lines under each job, project descriptions, and certifications. Do not limit extraction to just the Skills section.

Return a JSON object with this exact schema:
{{
    "contact": {{
        "name": "Full name or null",
        "email": "Email address or null",
        "phone": "Phone number or null",
        "location": "City/Country or null",
        "linkedin": "LinkedIn URL or null"
    }},
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "job_title": "Title",
            "company": "Company name",
            "start_date": "Start date as written",
            "end_date": "End date as written or 'Present'",
            "description": "Brief description of role/responsibilities"
        }}
    ],
    "education": [
        {{
            "degree": "Degree name",
            "institution": "School/University name",
            "year": "Graduation year or date range",
            "field": "Field of study or null"
        }}
    ],
    "certifications": ["cert1", "cert2", ...],
    "summary": "Professional summary/objective if present, or null"
}}

CV TEXT:
---
{cv_text}
---

Return ONLY the JSON object, nothing else."""

K_MAX_CV_TEXT_LENGTH = 6000


class OpenAICVParser:
    """Uses GPT-4o-mini to parse structured data from CV text."""

    # /*
    # * function name: __init__()
    # * Description: Initialize the OpenAI CV parser with API credentials.
    # * Parameter: api_key : str : OpenAI API key for authentication.
    # *            model : str : OpenAI model to use (default gpt-4o-mini).
    # * return: None
    # */
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    # /*
    # * function name: parse_cv()
    # * Description: Send raw CV text to OpenAI and get structured data back.
    # *              Raises ParsingError if the API call fails or returns invalid JSON.
    # * Parameter: raw_text : str : Raw text extracted from a CV file.
    # * return: dict : Parsed CV data containing contact, skills, experience,
    # *                education, certifications, and summary.
    # */
    def parse_cv(self, raw_text: str) -> dict:
        prompt = K_USER_PROMPT_TEMPLATE.format(cv_text=raw_text[:K_MAX_CV_TEXT_LENGTH])

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": K_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )

            parsed = json.loads(response.choices[0].message.content)
            return self._validate_output(parsed)

        except json.JSONDecodeError as e:
            raise ParsingError(f"Failed to parse OpenAI response as JSON: {e}")
        except Exception as e:
            raise ParsingError(f"OpenAI API error: {e}")

    # /*
    # * function name: _validate_output()
    # * Description: Ensure the parsed output has all required fields. Adds
    # *              missing keys with default values so downstream code is safe.
    # * Parameter: parsed : dict : Raw parsed dictionary from OpenAI response.
    # * return: dict : Validated dictionary with all required keys present.
    # */
    @staticmethod
    def _validate_output(parsed: dict) -> dict:
        K_REQUIRED_KEYS = ["contact", "skills", "experience", "education"]
        for key in K_REQUIRED_KEYS:
            if key not in parsed:
                parsed[key] = {} if key == "contact" else []

        if isinstance(parsed.get("skills"), list):
            parsed["skills"] = [str(s).strip() for s in parsed["skills"] if s]
        else:
            parsed["skills"] = []

        if "certifications" not in parsed:
            parsed["certifications"] = []

        if "summary" not in parsed:
            parsed["summary"] = None

        return parsed


# /*
# * function name: get_parser()
# * Description: Factory function that creates an OpenAICVParser if the
# *              OPENAI_API_KEY environment variable is configured.
# * Parameter: void : This function does not take any parameters.
# * return: Optional[OpenAICVParser] : Parser instance or None if key is missing.
# */
def get_parser() -> Optional[OpenAICVParser]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. CV parsing will use fallback mode.")
        return None
    return OpenAICVParser(api_key=api_key)


# /*
# * function name: fallback_parse()
# * Description: Returns a minimal result structure when OpenAI API is unavailable.
# *              All parsed fields are set to None or empty lists.
# * Parameter: raw_text : str : The raw CV text (unused but kept for interface consistency).
# * return: dict : Fallback dictionary with _fallback flag set to True.
# */
def fallback_parse(raw_text: str) -> dict:
    return {
        "contact": {"name": None, "email": None, "phone": None, "location": None, "linkedin": None},
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "summary": None,
        "_fallback": True,
    }
