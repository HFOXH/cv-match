import json
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from ..exceptions import ParsingError
from dotenv import load_dotenv
from services.openai_retry import retry_openai_call
from prompts import K_CV_PARSER_SYSTEM_PROMPT, K_CV_PARSER_USER_PROMPT
from config import CV_PARSER_MODEL, MAX_CV_TEXT_LENGTH

load_dotenv()

logger = logging.getLogger(__name__)

K_MAX_CV_TEXT_LENGTH = MAX_CV_TEXT_LENGTH


class OpenAICVParser:
    """Uses OpenAI chat completions to parse structured data from CV text."""

    def __init__(self, api_key: str, model: str = CV_PARSER_MODEL):
        """Initialize the OpenAI CV parser with API credentials.

        Args:
            api_key: OpenAI API key for authentication.
            model: OpenAI model to use (default gpt-4o-mini).
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def parse_cv(self, raw_text: str) -> dict:
        """Send raw CV text to OpenAI and get structured data back.

        Raises ParsingError if the API call fails or returns invalid JSON.

        Args:
            raw_text: Raw text extracted from a CV file.

        Returns:
            Parsed CV data containing contact, skills, experience, education,
            certifications, and summary.
        """
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

    @staticmethod
    def _validate_output(parsed: dict) -> dict:
        """Ensure the parsed output has all required fields.

        Adds missing keys with default values so downstream code is safe.

        Args:
            parsed: Raw parsed dictionary from OpenAI response.

        Returns:
            Validated dictionary with all required keys present.
        """
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


def get_parser() -> Optional[OpenAICVParser]:
    """Factory function that creates an OpenAICVParser.

    Returns:
        Parser instance if OPENAI_API_KEY is set in the environment,
        otherwise None.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. CV parsing is unavailable.")
        return None
    return OpenAICVParser(api_key=api_key)
