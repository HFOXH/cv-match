from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from typing import Dict, Any, Optional

from embedding.hybrid_encoder import HybridEncoder

logger = logging.getLogger(__name__)


class MatchingService:
    """Service layer for CV-JD matching.

    Uses HybridEncoder for embedding generation and provides
    similarity computation methods. Task 4 will extend this with
    weighted scoring, Jaccard, and calibration.
    """

    def __init__(self):
        self.hybrid_encoder = HybridEncoder()

    def encode_cv(
        self, cv_id: str, normalized_cv: dict, raw_text: str,
        parsing_method: str = "openai",
    ) -> dict:
        """Encode a CV using the hybrid encoder."""
        return self.hybrid_encoder.encode_cv(cv_id, normalized_cv, raw_text, parsing_method)

    def encode_jd(self, preprocessed_jd: dict) -> dict:
        """Encode a job description using the hybrid encoder."""
        return self.hybrid_encoder.encode_job_description(preprocessed_jd)

    def compute_match(self, cv_vectors: dict, jd_vectors: dict) -> dict:
        """Compute similarity scores between encoded CV and JD.

        Returns a dict of component scores. Task 4 will replace
        the weighting with a full SimilarityEngine.
        """
        is_fallback = cv_vectors.get("_fallback", False)

        # Overall semantic similarity (OpenAI embeddings)
        overall_sim = self._cosine_sim(
            cv_vectors["section_embeddings"].get("overall"),
            jd_vectors["section_embeddings"].get("overall"),
        )

        # Section-level similarities (only in non-fallback mode)
        section_sims = {}
        if not is_fallback:
            section_sims["skills_semantic"] = self._cosine_sim(
                cv_vectors["section_embeddings"].get("skills"),
                jd_vectors["section_embeddings"].get("skills"),
            )
            section_sims["experience"] = self._cosine_sim(
                cv_vectors["section_embeddings"].get("experience"),
                jd_vectors["section_embeddings"].get("overall"),
            )
            section_sims["education"] = self._cosine_sim(
                cv_vectors["section_embeddings"].get("education"),
                jd_vectors["section_embeddings"].get("overall"),
            )

        # TF-IDF similarity
        tfidf_result = self.hybrid_encoder.compute_tfidf_vectors(
            cv_vectors.get("raw_text", ""),
            jd_vectors.get("cleaned_text", ""),
        )
        tfidf_sim = 0.0
        if tfidf_result["cv_vector"] is not None and tfidf_result["jd_vector"] is not None:
            tfidf_sim = self._cosine_sim(
                tfidf_result["cv_vector"].toarray().flatten(),
                tfidf_result["jd_vector"].toarray().flatten(),
            )

        # Weighted average (Task 4 will replace with calibrated scoring)
        if is_fallback:
            match_score = (overall_sim * 0.55 + tfidf_sim * 0.45) * 100
        else:
            match_score = (
                overall_sim * 0.35
                + section_sims.get("skills_semantic", 0) * 0.25
                + section_sims.get("experience", 0) * 0.20
                + section_sims.get("education", 0) * 0.05
                + tfidf_sim * 0.15
            ) * 100

        return {
            "match_score": round(match_score, 2),
            "overall_similarity": round(overall_sim * 100, 2),
            "section_similarities": {k: round(v * 100, 2) for k, v in section_sims.items()},
            "tfidf_similarity": round(tfidf_sim * 100, 2),
            "cv_skills": cv_vectors.get("skills_list", []),
            "jd_skills": jd_vectors.get("skills_list", []),
            "_fallback": is_fallback,
        }

    @staticmethod
    def _cosine_sim(vec1, vec2) -> float:
        """Compute cosine similarity between two vectors. Returns 0.0 if either is None."""
        if vec1 is None or vec2 is None:
            return 0.0
        v1 = np.array(vec1).reshape(1, -1)
        v2 = np.array(vec2).reshape(1, -1)
        return float(cosine_similarity(v1, v2)[0][0])
