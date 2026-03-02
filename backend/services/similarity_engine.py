import math
import logging
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

K_SIGMOID_STEEPNESS = 12
K_SIGMOID_MIDPOINT = 0.45

K_WEIGHTS_FULL = {
    "skills_jaccard": 0.30,
    "skills_semantic": 0.10,
    "sbert_overall": 0.25,
    "experience_match": 0.20,
    "education_match": 0.05,
    "tfidf_overall": 0.10,
}

K_WEIGHTS_FALLBACK = {
    "sbert_overall": 0.55,
    "tfidf_overall": 0.45,
}

K_SCORE_BANDS = [
    (90, 100, "Excellent Match", "Strong candidate — definitely apply", "green"),
    (75, 89, "Good Match", "Good candidate — apply with confidence", "light-green"),
    (60, 74, "Moderate Match", "Consider applying — highlight transferable skills", "yellow"),
    (40, 59, "Weak Match", "Significant gaps — apply cautiously", "orange"),
    (0, 39, "Poor Match", "Not recommended — major misalignment", "red"),
]


class SimilarityEngine:
    """Core scoring engine combining Jaccard skill matching, cosine similarity,
    TF-IDF keyword matching, and sigmoid calibration into a match report."""

    def calculate_match(
        self,
        cv_vectors: dict,
        jd_vectors: dict,
        tfidf_sim: float,
        is_fallback: bool = False,
    ) -> dict:
        """Master scoring function. Returns full match report dict."""
        if is_fallback:
            return self._calculate_fallback(cv_vectors, jd_vectors, tfidf_sim)

        skill_details = self.calculate_jaccard(
            cv_vectors.get("skills_list", []),
            jd_vectors.get("skills_list", []),
        )

        section_sims = self._section_similarities(cv_vectors, jd_vectors)

        overall_sbert = self._cosine_sim(
            cv_vectors["section_embeddings"].get("overall"),
            jd_vectors["section_embeddings"].get("overall"),
        )

        raw_scores = {
            "skills_jaccard": skill_details["score"],
            "skills_semantic": section_sims.get("skills_semantic", 0.0),
            "sbert_overall": overall_sbert,
            "experience_match": section_sims.get("experience", 0.0),
            "education_match": section_sims.get("education", 0.0),
            "tfidf_overall": tfidf_sim,
        }

        weighted_sum = sum(
            raw_scores[k] * K_WEIGHTS_FULL[k] for k in K_WEIGHTS_FULL
        )

        match_percentage = self.calibrate_score(weighted_sum)

        return self._build_report(
            match_percentage=match_percentage,
            raw_scores=raw_scores,
            skill_details=skill_details,
            weights_used=K_WEIGHTS_FULL,
            is_fallback=False,
        )

    @staticmethod
    def _fuzzy_match(skill_a: str, skill_b: str) -> bool:
        """Check if two skills match using substring or string similarity."""
        if skill_a in skill_b or skill_b in skill_a:
            return True
        return SequenceMatcher(None, skill_a, skill_b).ratio() >= 0.8

    @staticmethod
    def calculate_jaccard(cv_skills: list, jd_skills: list) -> dict:
        """Compare skill sets with fuzzy matching. Returns score plus matched/missing details."""
        cv_set = {s.lower().strip() for s in cv_skills if s}
        jd_set = {s.lower().strip() for s in jd_skills if s}

        # Exact matches first
        exact_matched = cv_set & jd_set
        remaining_cv = cv_set - exact_matched
        remaining_jd = jd_set - exact_matched

        # Fuzzy matching on remaining skills
        fuzzy_matched_jd = set()
        fuzzy_matched_cv = set()
        for jd_skill in remaining_jd:
            for cv_skill in remaining_cv:
                if cv_skill not in fuzzy_matched_cv and SimilarityEngine._fuzzy_match(cv_skill, jd_skill):
                    fuzzy_matched_jd.add(jd_skill)
                    fuzzy_matched_cv.add(cv_skill)
                    break

        matched = exact_matched | fuzzy_matched_jd
        missing = remaining_jd - fuzzy_matched_jd
        extra = remaining_cv - fuzzy_matched_cv
        union = cv_set | jd_set

        score = len(matched) / len(union) if union else 0.0

        return {
            "score": score,
            "matched_skills": sorted(matched),
            "missing_skills": sorted(missing),
            "extra_skills": sorted(extra),
            "cv_skills_count": len(cv_set),
            "job_skills_count": len(jd_set),
            "matched_count": len(matched),
        }

    @staticmethod
    def calibrate_score(raw_score: float) -> float:
        """Convert raw similarity (typically 0.3-0.8) to intuitive 0-100 percentage."""
        calibrated = 1.0 / (1.0 + math.exp(-K_SIGMOID_STEEPNESS * (raw_score - K_SIGMOID_MIDPOINT)))
        percentage = calibrated * 100.0
        return round(max(0.0, min(100.0, percentage)), 1)

    @staticmethod
    def get_score_band(percentage: float) -> dict:
        """Return rating, recommendation, and color for a given percentage."""
        for low, high, rating, recommendation, color in K_SCORE_BANDS:
            if low <= percentage <= high:
                return {"rating": rating, "recommendation": recommendation, "color": color}
        return {"rating": "Poor Match", "recommendation": "Not recommended — major misalignment", "color": "red"}

    @staticmethod
    def _cosine_sim(vec1, vec2) -> float:
        if vec1 is None or vec2 is None:
            return 0.0
        v1 = np.array(vec1).reshape(1, -1)
        v2 = np.array(vec2).reshape(1, -1)
        return float(cosine_similarity(v1, v2)[0][0])

    def _section_similarities(self, cv_vectors: dict, jd_vectors: dict) -> dict:
        cv_emb = cv_vectors["section_embeddings"]
        jd_emb = jd_vectors["section_embeddings"]
        return {
            "skills_semantic": self._cosine_sim(cv_emb.get("skills"), jd_emb.get("skills")),
            "experience": self._cosine_sim(cv_emb.get("experience"), jd_emb.get("overall")),
            "education": self._cosine_sim(cv_emb.get("education"), jd_emb.get("overall")),
        }

    def _calculate_fallback(self, cv_vectors, jd_vectors, tfidf_sim) -> dict:
        overall_sbert = self._cosine_sim(
            cv_vectors["section_embeddings"].get("overall"),
            jd_vectors["section_embeddings"].get("overall"),
        )
        raw_scores = {
            "sbert_overall": overall_sbert,
            "tfidf_overall": tfidf_sim,
        }
        weighted_sum = sum(
            raw_scores[k] * K_WEIGHTS_FALLBACK[k] for k in K_WEIGHTS_FALLBACK
        )
        match_percentage = self.calibrate_score(weighted_sum)

        return self._build_report(
            match_percentage=match_percentage,
            raw_scores=raw_scores,
            skill_details=None,
            weights_used=K_WEIGHTS_FALLBACK,
            is_fallback=True,
        )

    def _build_report(
        self,
        match_percentage: float,
        raw_scores: dict,
        skill_details: Optional[dict],
        weights_used: dict,
        is_fallback: bool,
    ) -> dict:
        band = self.get_score_band(match_percentage)

        report = {
            "match_percentage": match_percentage,
            "match_rating": band["rating"],
            "recommendation": band["recommendation"],
            "confidence": "reduced" if is_fallback else "high",
            "raw_scores": raw_scores,
            "weights_used": weights_used,
            "skill_details": skill_details,
            "breakdown": {},
            "strengths": [],
            "gaps": [],
            "_fallback": is_fallback,
        }

        report["breakdown"]["overall_semantic"] = {
            "score": round(raw_scores.get("sbert_overall", 0) * 100, 1),
            "weight": f"{int(weights_used.get('sbert_overall', 0) * 100)}%",
        }

        report["breakdown"]["tfidf"] = {
            "score": round(raw_scores.get("tfidf_overall", 0) * 100, 1),
            "weight": f"{int(weights_used.get('tfidf_overall', 0) * 100)}%",
        }

        if not is_fallback and skill_details:
            report["breakdown"]["skills"] = {
                "score": round(skill_details["score"] * 100, 1),
                "matched": skill_details["matched_skills"],
                "missing": skill_details["missing_skills"],
                "matched_count": f"{skill_details['matched_count']}/{skill_details['job_skills_count']}",
                "weight": f"{int(weights_used.get('skills_jaccard', 0) * 100)}%",
            }

            report["breakdown"]["experience"] = {
                "score": round(raw_scores.get("experience_match", 0) * 100, 1),
                "weight": f"{int(weights_used.get('experience_match', 0) * 100)}%",
            }

            report["breakdown"]["education"] = {
                "score": round(raw_scores.get("education_match", 0) * 100, 1),
                "weight": f"{int(weights_used.get('education_match', 0) * 100)}%",
            }

            if skill_details["matched_skills"]:
                top = skill_details["matched_skills"][:5]
                report["strengths"].append(f"Strong match on: {', '.join(top)}")

            if raw_scores.get("experience_match", 0) > 0.7:
                report["strengths"].append("Experience aligns well with the role")

            if skill_details["missing_skills"]:
                top_missing = skill_details["missing_skills"][:5]
                report["gaps"].append(f"Missing skills: {', '.join(top_missing)}")

            if raw_scores.get("experience_match", 0) < 0.4:
                report["gaps"].append("Experience may not align closely with requirements")

        return report
