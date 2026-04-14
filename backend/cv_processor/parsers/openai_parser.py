import json
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from ..exceptions import ParsingError
from dotenv import load_dotenv
from services.openai_retry import retry_openai_call
from prompts import K_CV_PARSER_SYSTEM_PROMPT, K_CV_PARSER_USER_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)

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
        prompt = K_CV_PARSER_USER_PROMPT.format(cv_text=raw_text[:K_MAX_CV_TEXT_LENGTH])

        try:
            response = retry_openai_call(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": K_CV_PARSER_SYSTEM_PROMPT},
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
        logger.warning("OPENAI_API_KEY not set. CV parsing is unavailable.")
        return None
    return OpenAICVParser(api_key=api_key)
