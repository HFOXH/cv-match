import json
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

from .cleaner import TextCleaner
from services.openai_retry import retry_openai_call
from prompts import K_NORMALIZATION_SYSTEM_PROMPT, K_NORMALIZATION_USER_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)


class CVDataNormalizer:
    """OpenAI-powered normalization for parsed CV data.

    Uses OpenAI to intelligently normalize skills (handling abbreviations,
    variations, typos) and generate clean embedding text from CV sections.
    Logs errors if OpenAI is unavailable or fails.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the CV data normalizer with OpenAI client.

        Args:
            openai_api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            logger.error("No OpenAI API key provided. CV normalization will not work.")

        logger.info("CVDataNormalizer initialized")

    def normalize(self, parsed_cv: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize OpenAI-parsed CV data for downstream matching.

        Uses OpenAI for intelligent normalization. Returns empty result and
        logs error if OpenAI is unavailable or fails.

        Args:
            parsed_cv: Dictionary from OpenAI parser with keys: contact, skills,
                experience, education, certifications, summary.

        Returns:
            Normalized data with skills, experience_text, education_text, and
            full_text_for_embedding.
        """
        if not self.client:
            logger.error("OpenAI client not available. Cannot normalize CV data.")
            return self._empty_result()

        try:
            cv_data_str = json.dumps(parsed_cv, indent=2, default=str)
            prompt = K_NORMALIZATION_USER_PROMPT.format(cv_data=cv_data_str)

            response = retry_openai_call(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": K_NORMALIZATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=1500,
            )

            result = response.choices[0].message.content.strip()
            result = result.replace("```json", "").replace("```", "").strip()
            normalized = json.loads(result)

            return {
                "skills": TextCleaner.normalize_skills(normalized.get("skills", [])),
                "experience_text": normalized.get("experience_text", ""),
                "education_text": normalized.get("education_text", ""),
                "full_text_for_embedding": normalized.get("full_text_for_embedding", ""),
            }

        except json.JSONDecodeError as e:
            logger.error("Failed to parse OpenAI response as JSON: %s", e)
            return self._empty_result()
        except Exception as e:
            logger.error("OpenAI API call failed: %s", e)
            return self._empty_result()

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            "skills": [],
            "experience_text": "",
            "education_text": "",
            "full_text_for_embedding": "",
        }
