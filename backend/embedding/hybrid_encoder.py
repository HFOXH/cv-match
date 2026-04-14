import hashlib
import logging
from typing import Dict, Any, Optional

from .openai_encoder import OpenAIEncoder
from .section_embeddings import SectionEmbeddingGenerator
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class HybridEncoder:
    """Orchestrator for OpenAI-based section embeddings with SQLite caching."""

    def __init__(self, db_path: str = "vectors.db", openai_api_key: Optional[str] = None):
        self.openai_encoder = OpenAIEncoder(openai_api_key=openai_api_key)
        self.section_generator = SectionEmbeddingGenerator(self.openai_encoder)
        self.vector_store = VectorStore(db_path=db_path)
        logger.info("HybridEncoder initialized")

    def encode_cv(
        self,
        cv_id: str,
        normalized_cv: Dict[str, Any],
        raw_text: str,
    ) -> Dict[str, Any]:
        """Generate section embeddings for a CV from its normalized data."""
        cached = self.vector_store.get_cv_vectors(cv_id)
        # Skip cache entries that lack a valid overall embedding (e.g. rows left
        # over from the previous fallback mode). Force regeneration.
        if cached and cached.get("section_embeddings", {}).get("overall") is not None:
            logger.info("Using cached vectors for cv_id=%s", cv_id)
            return {
                "cv_id": cv_id,
                "section_embeddings": cached["section_embeddings"],
                "skills_list": cached["skills_list"],
                "raw_text": raw_text,
            }
        if cached:
            logger.warning("Discarding stale cache entry for cv_id=%s (missing overall embedding)", cv_id)

        section_embeddings = self.section_generator.generate_cv_section_embeddings(normalized_cv)
        skills_list = normalized_cv.get("skills", [])

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
