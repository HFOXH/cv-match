import json
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

from .cleaner import TextCleaner

load_dotenv()

logger = logging.getLogger(__name__)

K_NORMALIZATION_SYSTEM_PROMPT = (
    "You are a CV data normalizer. Return only valid JSON, no markdown."
)

K_NORMALIZATION_USER_PROMPT = """Normalize this parsed CV data for job matching purposes.
Return ONLY valid JSON with these fields:

{{
    "skills": ["list of normalized, deduplicated skill names in lowercase"],
    "experience_text": "single paragraph combining all work experience for semantic embedding",
    "education_text": "single paragraph combining all education for semantic embedding",
    "full_text_for_embedding": "complete natural-language summary of the candidate combining all sections"
}}

Rules for skills normalization:
- Lowercase all skill names
- Expand common abbreviations from ANY industry (JS -> javascript, ML -> machine learning, AWS -> amazon web services, POS -> point of sale, CPR -> cardiopulmonary resuscitation, HVAC -> heating ventilation and air conditioning, etc.)
- Merge duplicates
- Keep both technical/hard skills AND soft skills
- Remove non-skill items if any
- Split compound skills into individual entries (e.g., "teamwork and communication" -> "teamwork", "communication")
- Infer implicit skills clearly demonstrated by experience (e.g., working retail -> "multitasking", "time management", "attention to detail"; managing stock -> "inventory management"; serving customers -> "customer service")
- Include common soft skills that are clearly demonstrated by the experience even if not explicitly listed
- This applies to ALL industries: retail, healthcare, trades, hospitality, IT, education, manufacturing, etc.

Rules for text fields:
- Write experience_text as a factual summary of capabilities and domains: focus on years of experience, types of roles held, industries/domains, and key responsibilities. Examples: "2+ years of retail experience as a store associate at a grocery chain. Handled customer service, food preparation, stock rotation, and merchandising." or "5 years of nursing experience in acute care settings. Skilled in patient assessment, medication administration, and electronic health records."
- Write education_text as a factual summary of qualifications: focus on degree levels, fields of study, and institutions. Examples: "Software Engineering Technology diploma from Conestoga College. Currently pursuing AI and ML at Cambrian College." or "Bachelor of Science in Nursing from University of Toronto. CPR and First Aid certified."
- The full_text_for_embedding should read like a professional profile summary
- All text fields should use neutral, factual language that works for both CV-to-JD and JD-to-CV comparison

Parsed CV data:
{cv_data}"""


class CVDataNormalizer:
    """OpenAI-powered normalization for parsed CV data.

    Uses OpenAI to intelligently normalize skills (handling abbreviations,
    variations, typos) and generate clean embedding text from CV sections.
    Logs errors if OpenAI is unavailable or fails.
    """

    # /*
    # * function name: __init__()
    # * Description: Initialize the CV data normalizer with OpenAI client.
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
            logger.error("No OpenAI API key provided. CV normalization will not work.")

        logger.info("CVDataNormalizer initialized")

    # /*
    # * function name: normalize()
    # * Description: Normalize OpenAI-parsed CV data for downstream matching.
    # *              Uses OpenAI for intelligent normalization. Returns empty
    # *              result and logs error if OpenAI is unavailable or fails.
    # * Parameter: parsed_cv : dict : Dictionary from OpenAI parser with keys:
    # *              contact, skills, experience, education, certifications, summary.
    # * return: dict : Normalized data with skills, experience_text,
    # *              education_text, and full_text_for_embedding.
    # */
    def normalize(self, parsed_cv: Dict[str, Any]) -> Dict[str, Any]:
        if not self.client:
            logger.error("OpenAI client not available. Cannot normalize CV data.")
            return self._empty_result()

        try:
            cv_data_str = json.dumps(parsed_cv, indent=2, default=str)
            prompt = K_NORMALIZATION_USER_PROMPT.format(cv_data=cv_data_str)

            response = self.client.chat.completions.create(
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
