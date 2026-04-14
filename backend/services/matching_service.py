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

    def encode_cv(self, cv_id: str, normalized_cv: dict, raw_text: str) -> dict:
        """Encode a CV using the hybrid encoder."""
        return self.hybrid_encoder.encode_cv(cv_id, normalized_cv, raw_text)

    def encode_jd(self, preprocessed_jd: dict) -> dict:
        """Encode a job description using the hybrid encoder."""
        return self.hybrid_encoder.encode_job_description(preprocessed_jd)

    def compute_match(self, cv_vectors: dict, jd_vectors: dict) -> dict:
        """Compute similarity scores between encoded CV and JD.

        Delegates scoring to SimilarityEngine. Returns full match report
        plus backward-compatible fields for the existing frontend.
        """
        report = self.similarity_engine.calculate_match(
            cv_vectors=cv_vectors,
            jd_vectors=jd_vectors,
        )

        # Add backward-compat fields for the existing frontend
        raw = report.get("raw_scores", {})
        breakdown = report.get("breakdown", {})
        skills_match = breakdown.get("skills", {}).get("score", round(raw.get("skills_semantic", 0) * 100, 2))
        report["match_score"] = report["match_percentage"]
        report["overall_similarity"] = round(raw.get("sbert_overall", 0) * 100, 2)
        report["section_similarities"] = {
            "skills_match": skills_match,
            "skills_semantic": skills_match,
            "experience": breakdown.get("experience", {}).get("score", round(raw.get("experience_match", 0) * 100, 2)),
            "education": breakdown.get("education", {}).get("score", round(raw.get("education_match", 0) * 100, 2)),
        }
        report["cv_skills"] = cv_vectors.get("skills_list", [])
        report["jd_skills"] = jd_vectors.get("skills_list", [])

        return report
