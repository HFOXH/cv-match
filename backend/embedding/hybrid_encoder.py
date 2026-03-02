import hashlib
import logging
from typing import Dict, Any, Optional

from .tfidf_encoder import TFIDFEncoder
from .openai_encoder import OpenAIEncoder
from .section_embeddings import SectionEmbeddingGenerator
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

K_FALLBACK_MAX_TEXT_LENGTH = 8000


class HybridEncoder:
    """Orchestrator combining TF-IDF + OpenAI embeddings + section-level comparison.

    Handles both normal mode (structured CV data) and fallback mode
    (raw text only, when parsing failed).
    """

    def __init__(self, db_path: str = "vectors.db", openai_api_key: Optional[str] = None):
        self.tfidf_encoder = TFIDFEncoder()
        self.openai_encoder = OpenAIEncoder(openai_api_key=openai_api_key)
        self.section_generator = SectionEmbeddingGenerator(self.openai_encoder)
        self.vector_store = VectorStore(db_path=db_path)
        logger.info("HybridEncoder initialized")

    def encode_cv(
        self,
        cv_id: str,
        normalized_cv: Dict[str, Any],
        raw_text: str,
        parsing_method: str = "openai",
    ) -> Dict[str, Any]:
        """Generate all embeddings for a CV.

        Uses structured data for section embeddings when available.
        Falls back to overall-only embedding when parsing failed.
        """
        is_fallback = parsing_method == "fallback" or self._is_empty_normalization(normalized_cv)

        if is_fallback:
            return self._encode_cv_fallback(cv_id, raw_text)

        # Check cache first
        cached = self.vector_store.get_cv_vectors(cv_id)
        if cached:
            logger.info("Using cached vectors for cv_id=%s", cv_id)
            return {
                "cv_id": cv_id,
                "section_embeddings": cached["section_embeddings"],
                "skills_list": cached["skills_list"],
                "raw_text": raw_text,
                "_fallback": cached["is_fallback"],
            }

        # Generate section embeddings from structured data
        section_embeddings = self.section_generator.generate_cv_section_embeddings(normalized_cv)
        skills_list = normalized_cv.get("skills", [])

        # Store in SQLite
        text_hash = hashlib.md5(raw_text.encode()).hexdigest()
        self.vector_store.save_cv_vectors(
            cv_id=cv_id,
            section_embeddings=section_embeddings,
            skills_list=skills_list,
            raw_text_hash=text_hash,
            is_fallback=False,
        )

        return {
            "cv_id": cv_id,
            "section_embeddings": section_embeddings,
            "skills_list": skills_list,
            "raw_text": raw_text,
            "_fallback": False,
        }

    def _encode_cv_fallback(self, cv_id: str, raw_text: str) -> Dict[str, Any]:
        """Generate embeddings when OpenAI parsing failed.
        Only overall embedding available -- no section breakdown.
        """
        logger.warning("Using fallback encoding for cv_id=%s (no structured data)", cv_id)

        truncated = raw_text[:K_FALLBACK_MAX_TEXT_LENGTH]
        overall_embedding = self.openai_encoder.encode(truncated)

        section_embeddings = {
            "overall": overall_embedding,
            "skills": None,
            "experience": None,
            "education": None,
        }

        text_hash = hashlib.md5(raw_text.encode()).hexdigest()
        self.vector_store.save_cv_vectors(
            cv_id=cv_id,
            section_embeddings=section_embeddings,
            skills_list=[],
            raw_text_hash=text_hash,
            is_fallback=True,
        )

        return {
            "cv_id": cv_id,
            "section_embeddings": section_embeddings,
            "skills_list": [],
            "raw_text": raw_text,
            "_fallback": True,
        }

    def encode_job_description(self, preprocessed_jd: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all embeddings for a job description."""
        section_embeddings = self.section_generator.generate_jd_section_embeddings(preprocessed_jd)

        skills_list = (
            preprocessed_jd.get("required_skills", [])
            + preprocessed_jd.get("preferred_skills", [])
        )

        return {
            "section_embeddings": section_embeddings,
            "skills_list": skills_list,
            "cleaned_text": preprocessed_jd.get("cleaned_text", ""),
        }

    def compute_tfidf_vectors(self, cv_text: str, jd_text: str) -> Dict[str, Any]:
        """Compute TF-IDF vectors for a CV-JD pair.
        Called at comparison time because TF-IDF requires fitting on both docs together.
        """
        return self.tfidf_encoder.fit_and_transform(cv_text, jd_text)

    @staticmethod
    def _is_empty_normalization(normalized_cv: Dict[str, Any]) -> bool:
        return (
            not normalized_cv.get("skills")
            and not normalized_cv.get("experience_text")
            and not normalized_cv.get("education_text")
            and not normalized_cv.get("full_text_for_embedding")
        )
