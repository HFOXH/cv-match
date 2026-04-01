from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

from embedding.hybrid_encoder import HybridEncoder
from services.similarity_engine import SimilarityEngine

logger = logging.getLogger(__name__)


class MatchingService:
    """Service layer for CV-JD matching.

    Uses HybridEncoder for embedding generation and
    SimilarityEngine for scoring, calibration, and report generation.
    """

    def __init__(self):
        self.hybrid_encoder = HybridEncoder()
        self.similarity_engine = SimilarityEngine()

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

        Delegates scoring to SimilarityEngine. Returns full match report
        plus backward-compatible fields for the existing frontend.
        """
        is_fallback = cv_vectors.get("_fallback", False)

        # Compute TF-IDF similarity only for fallback mode
        tfidf_sim = 0.0
        if is_fallback:
            tfidf_result = self.hybrid_encoder.compute_tfidf_vectors(
                cv_vectors.get("raw_text", ""),
                jd_vectors.get("cleaned_text", ""),
            )
            if tfidf_result["cv_vector"] is not None and tfidf_result["jd_vector"] is not None:
                tfidf_sim = self._cosine_sim(
                    tfidf_result["cv_vector"].toarray().flatten(),
                    tfidf_result["jd_vector"].toarray().flatten(),
                )

        # Delegate to SimilarityEngine
        report = self.similarity_engine.calculate_match(
            cv_vectors=cv_vectors,
            jd_vectors=jd_vectors,
            tfidf_sim=tfidf_sim,
            is_fallback=is_fallback,
        )

        # Add backward-compat fields for the existing frontend
        raw = report.get("raw_scores", {})
        report["match_score"] = report["match_percentage"]
        report["overall_similarity"] = round(raw.get("sbert_overall", 0) * 100, 2)
        report["section_similarities"] = {}
        if not is_fallback:
            breakdown = report.get("breakdown", {})
            report["section_similarities"] = {
                "skills_semantic": breakdown.get("skills", {}).get("score", round(raw.get("skills_semantic", 0) * 100, 2)),
                "experience": breakdown.get("experience", {}).get("score", round(raw.get("experience_match", 0) * 100, 2)),
                "education": breakdown.get("education", {}).get("score", round(raw.get("education_match", 0) * 100, 2)),
            }
        report["cv_skills"] = cv_vectors.get("skills_list", [])
        report["jd_skills"] = jd_vectors.get("skills_list", [])

        return report

    @staticmethod
    def _cosine_sim(vec1, vec2) -> float:
        """Compute cosine similarity between two vectors. Returns 0.0 if either is None."""
        if vec1 is None or vec2 is None:
            return 0.0
        v1 = np.array(vec1).reshape(1, -1)
        v2 = np.array(vec2).reshape(1, -1)
        return float(cosine_similarity(v1, v2)[0][0])
