import json
import math
import os
import re
import logging
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional

import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from services.openai_retry import retry_openai_call
from prompts import K_SEMANTIC_MATCH_PROMPT
from config import (
    SEMANTIC_MATCH_MODEL,
    SIGMOID_STEEPNESS,
    SIGMOID_MIDPOINT,
    WEIGHTS,
)

load_dotenv()

logger = logging.getLogger(__name__)

K_SIGMOID_STEEPNESS = SIGMOID_STEEPNESS
K_SIGMOID_MIDPOINT = SIGMOID_MIDPOINT
K_WEIGHTS_FULL = WEIGHTS

K_SCORE_BANDS = [
    (90, 100, "Excellent Match", "Strong candidate — definitely apply", "green"),
    (75, 90, "Good Match", "Good candidate — apply with confidence", "light-green"),
    (60, 75, "Moderate Match", "Consider applying — highlight transferable skills", "yellow"),
    (40, 60, "Weak Match", "Significant gaps — apply cautiously", "orange"),
    (0, 40, "Poor Match", "Not recommended — major misalignment", "red"),
]


class SimilarityEngine:
    """Core scoring engine combining Jaccard skill matching, cosine similarity,
    and sigmoid calibration into a match report."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("No OpenAI API key — semantic skill matching disabled")

    # Education level hierarchy for comparison (ordered highest first for matching)
    K_EDUCATION_LEVELS = [
        (5, ["phd", "doctorate", "doctoral"]),
        (4, ["master's", "master", "mba", "postgraduate", "post-graduate"]),
        (3, ["bachelor's", "bachelor", "b.sc", "b.a.", "b.eng", "bsc", "undergraduate degree"]),
        (2, ["diploma", "associate", "college", "technology", "technologist", "technician",
              "certificate", "certification", "vocational", "trade school", "community college",
              "polytechnic", "institute of technology"]),
        (1, ["high school", "ged", "secondary", "grade 12"]),
    ]

    def calculate_match(
        self,
        cv_vectors: dict,
        jd_vectors: dict,
    ) -> dict:
        """Master scoring function. Returns full match report dict."""
        skill_details = self.calculate_jaccard(
            cv_vectors.get("skills_list") or [],
            jd_vectors.get("skills_list") or [],
        )

        # Enhance with OpenAI semantic matching for remaining unmatched skills
        if skill_details["missing_skills"] and self.openai_client:
            try:
                skill_details = self._enhance_with_semantic_matching(skill_details)
            except Exception as e:
                logger.warning("Semantic matching enhancement failed, continuing: %s", e)

        section_sims = self._section_similarities(cv_vectors, jd_vectors)

        cv_sections = cv_vectors.get("section_embeddings") or {}
        jd_sections = jd_vectors.get("section_embeddings") or {}
        overall_sbert = self._cosine_sim(
            cv_sections.get("overall"),
            jd_sections.get("overall"),
        )

        # Boost education score if candidate meets or exceeds requirement
        education_sim = section_sims.get("education", 0.0)
        education_score = self._education_score(
            education_sim,
            cv_vectors.get("education_level"),
            jd_vectors.get("education_level"),
        )

        # Boost experience score if job titles/industry overlap
        experience_sim = section_sims.get("experience", 0.0)
        experience_score = self._experience_score(
            experience_sim,
            cv_vectors.get("job_titles", []),
            jd_vectors.get("job_title"),
        )

        raw_scores = {
            "skills_jaccard": skill_details["score"],
            "skills_semantic": section_sims.get("skills_semantic", 0.0),
            "sbert_overall": overall_sbert,
            "experience_match": experience_score,
            "education_match": education_score,
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
        )

    def _education_score(self, semantic_sim: float, cv_edu=None, jd_edu=None) -> float:
        """Score education: if candidate meets or exceeds requirement, boost the score."""
        if not isinstance(cv_edu, str) or not isinstance(jd_edu, str):
            return semantic_sim
        if not cv_edu.strip() or not jd_edu.strip():
            return semantic_sim

        cv_level = self._parse_education_level(cv_edu)
        jd_level = self._parse_education_level(jd_edu)

        if cv_level == 0 or jd_level == 0:
            return semantic_sim

        if cv_level >= jd_level:
            # Meets or exceeds — score at least 0.8, or keep semantic if higher
            return max(semantic_sim, 0.8)
        elif cv_level == jd_level - 1:
            # One level below — partial credit
            return max(semantic_sim, 0.5)
        else:
            return semantic_sim

    def _experience_score(self, semantic_sim: float, cv_titles=None, jd_title=None) -> float:
        """Boost experience score when job titles or roles directly overlap."""
        if not isinstance(jd_title, str) or not jd_title.strip():
            return semantic_sim
        if not isinstance(cv_titles, list) or not cv_titles:
            return semantic_sim

        jd_lower = jd_title.lower().strip()
        jd_words = set(jd_lower.split())

        best_overlap = 0.0
        for title in cv_titles:
            if not isinstance(title, str) or not title.strip():
                continue
            title_lower = title.lower().strip()
            if title_lower in jd_lower or jd_lower in title_lower:
                return max(semantic_sim, 0.85)
            title_words = set(title_lower.split())
            if title_words and jd_words:
                overlap = len(title_words & jd_words) / len(title_words | jd_words)
                best_overlap = max(best_overlap, overlap)

        if best_overlap >= 0.5:
            return max(semantic_sim, 0.75)
        elif best_overlap >= 0.25:
            return max(semantic_sim, 0.6)

        return semantic_sim

    def _parse_education_level(self, edu_text) -> int:
        """Extract education level number from text. Checks highest levels first."""
        if not isinstance(edu_text, str) or not edu_text.strip():
            return 0
        edu_lower = edu_text.lower().strip()
        for level, keywords in self.K_EDUCATION_LEVELS:
            for keyword in keywords:
                if keyword in edu_lower:
                    return level
        return 0

    @staticmethod
    def _fuzzy_match(skill_a: str, skill_b: str) -> bool:
        """Check if two skills match using word-boundary substring or string similarity."""
        shorter, longer = (skill_a, skill_b) if len(skill_a) <= len(skill_b) else (skill_b, skill_a)
        if len(shorter) >= 4 and re.search(r'(?:^|\b)' + re.escape(shorter) + r'(?:\b|$)', longer):
            return True
        return SequenceMatcher(None, skill_a, skill_b).ratio() >= 0.8

    @staticmethod
    def calculate_jaccard(cv_skills: list, jd_skills: list) -> dict:
        """Compare skill sets with fuzzy matching. Returns score plus matched/missing details."""
        cv_set = {s.lower().strip() for s in (cv_skills or []) if isinstance(s, str) and s.strip()}
        jd_set = {s.lower().strip() for s in (jd_skills or []) if isinstance(s, str) and s.strip()}

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

        score = len(matched) / len(jd_set) if jd_set else 0.0

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
            if low <= percentage < high:
                return {"rating": rating, "recommendation": recommendation, "color": color}
        if percentage >= 100:
            return {"rating": "Excellent Match", "recommendation": "Strong candidate — definitely apply", "color": "green"}
        return {"rating": "Poor Match", "recommendation": "Not recommended — major misalignment", "color": "red"}

    @staticmethod
    def _cosine_sim(vec1, vec2) -> float:
        if vec1 is None or vec2 is None:
            return 0.0
        try:
            v1 = np.asarray(vec1, dtype=float).reshape(1, -1)
            v2 = np.asarray(vec2, dtype=float).reshape(1, -1)
            if v1.shape[1] != v2.shape[1] or v1.size == 0 or v2.size == 0:
                return 0.0
            if np.any(np.isnan(v1)) or np.any(np.isnan(v2)):
                return 0.0
            sim = float(cosine_similarity(v1, v2)[0][0])
            if np.isnan(sim) or np.isinf(sim):
                return 0.0
            return sim
        except Exception as e:
            logger.warning("cosine similarity failed: %s", e)
            return 0.0

    def _section_similarities(self, cv_vectors: dict, jd_vectors: dict) -> dict:
        cv_emb = cv_vectors.get("section_embeddings") or {}
        jd_emb = jd_vectors.get("section_embeddings") or {}

        # Compare experience↔experience and education↔education when available,
        # fall back to comparing against JD overall if section not extracted
        jd_experience = jd_emb.get("experience") or jd_emb.get("overall")
        jd_education = jd_emb.get("education") or jd_emb.get("overall")

        return {
            "skills_semantic": self._cosine_sim(cv_emb.get("skills"), jd_emb.get("skills")),
            "experience": self._cosine_sim(cv_emb.get("experience"), jd_experience),
            "education": self._cosine_sim(cv_emb.get("education"), jd_education),
        }

    def _enhance_with_semantic_matching(self, skill_details: dict) -> dict:
        """Use OpenAI to find semantic matches among skills that exact+fuzzy missed."""
        missing = skill_details["missing_skills"]
        extra = skill_details["extra_skills"]

        if not missing or not extra:
            return skill_details

        semantic_pairs = self._semantic_skill_match(extra, missing)

        if not semantic_pairs:
            return skill_details

        newly_matched_jd = set()
        newly_matched_cv = set()
        for pair in semantic_pairs:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                continue
            cv_skill, jd_skill = pair
            if not isinstance(cv_skill, str) or not isinstance(jd_skill, str):
                continue
            cv_low = cv_skill.lower().strip()
            jd_low = jd_skill.lower().strip()
            if cv_low in {s.lower() for s in extra} and jd_low in {s.lower() for s in missing}:
                newly_matched_jd.add(jd_low)
                newly_matched_cv.add(cv_low)

        if not newly_matched_jd:
            return skill_details

        updated_matched = sorted(set(skill_details["matched_skills"]) | newly_matched_jd)
        updated_missing = sorted(set(skill_details["missing_skills"]) - newly_matched_jd)
        updated_extra = sorted(set(skill_details["extra_skills"]) - newly_matched_cv)
        matched_count = len(updated_matched)

        jd_total = matched_count + len(updated_missing)
        score = matched_count / jd_total if jd_total > 0 else 0.0

        logger.info("Semantic matching found %d additional pairs", len(newly_matched_jd))

        return {
            "score": score,
            "matched_skills": updated_matched,
            "missing_skills": updated_missing,
            "extra_skills": updated_extra,
            "cv_skills_count": skill_details["cv_skills_count"],
            "job_skills_count": skill_details["job_skills_count"],
            "matched_count": matched_count,
        }

    def _semantic_skill_match(self, cv_skills: list, jd_skills: list) -> list:
        """Send unmatched skills to GPT-4o-mini to find semantic equivalents."""
        prompt = K_SEMANTIC_MATCH_PROMPT.format(
            cv_skills=json.dumps(cv_skills),
            jd_skills=json.dumps(jd_skills),
        )

        try:
            response = retry_openai_call(
                self.openai_client.chat.completions.create,
                model=SEMANTIC_MATCH_MODEL,
                messages=[
                    {"role": "system", "content": "Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=500,
            )

            result = response.choices[0].message.content.strip()
            result = result.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(result)
            return parsed.get("matches", [])

        except Exception as e:
            logger.error("Semantic skill matching failed: %s", e)
            return []

    def _build_report(
        self,
        match_percentage: float,
        raw_scores: dict,
        skill_details: dict,
        weights_used: dict,
    ) -> dict:
        band = self.get_score_band(match_percentage)

        report = {
            "match_percentage": match_percentage,
            "match_rating": band["rating"],
            "recommendation": band["recommendation"],
            "confidence": "high",
            "raw_scores": raw_scores,
            "weights_used": weights_used,
            "skill_details": skill_details,
            "breakdown": {},
            "strengths": [],
            "gaps": [],
        }

        report["breakdown"]["overall_semantic"] = {
            "score": round(raw_scores.get("sbert_overall", 0) * 100, 1),
            "weight": f"{int(weights_used.get('sbert_overall', 0) * 100)}%",
        }

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
