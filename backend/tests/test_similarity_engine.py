from services.similarity_engine import (
    SimilarityEngine,
    K_SIGMOID_MIDPOINT,
    K_WEIGHTS_FULL,
    K_WEIGHTS_FALLBACK,
)

K_CV_SKILLS = ["python", "react", "docker", "fastapi", "machine learning"]
K_JD_SKILLS = ["python", "docker", "aws", "kubernetes", "machine learning"]

K_MATCHED = sorted({"python", "docker", "machine learning"})
K_MISSING = sorted({"aws", "kubernetes"})
K_EXTRA = sorted({"react", "fastapi"})


class TestJaccardSimilarity:

    def test_perfect_match(self):
        skills = ["python", "react", "docker"]
        result = SimilarityEngine.calculate_jaccard(skills, skills)
        assert result["score"] == 1.0
        assert result["matched_count"] == 3
        assert result["missing_skills"] == []

    def test_no_overlap(self):
        result = SimilarityEngine.calculate_jaccard(
            ["python", "react"], ["java", "spring"]
        )
        assert result["score"] == 0.0
        assert result["matched_count"] == 0
        assert len(result["missing_skills"]) == 2

    def test_partial_overlap(self):
        result = SimilarityEngine.calculate_jaccard(K_CV_SKILLS, K_JD_SKILLS)
        assert result["matched_skills"] == K_MATCHED
        assert result["missing_skills"] == K_MISSING
        assert result["extra_skills"] == K_EXTRA
        assert abs(result["score"] - 3 / 7) < 1e-9

    def test_empty_cv_skills(self):
        result = SimilarityEngine.calculate_jaccard([], ["python", "react"])
        assert result["score"] == 0.0
        assert result["matched_count"] == 0
        assert result["missing_skills"] == ["python", "react"]

    def test_empty_jd_skills(self):
        result = SimilarityEngine.calculate_jaccard(["python"], [])
        assert result["score"] == 0.0
        assert result["extra_skills"] == ["python"]

    def test_both_empty(self):
        result = SimilarityEngine.calculate_jaccard([], [])
        assert result["score"] == 0.0

    def test_case_insensitive(self):
        result = SimilarityEngine.calculate_jaccard(
            ["Python", "REACT"], ["python", "react"]
        )
        assert result["score"] == 1.0

    def test_strips_whitespace(self):
        result = SimilarityEngine.calculate_jaccard(
            [" python ", "react "], ["python", " react"]
        )
        assert result["score"] == 1.0

    def test_fuzzy_substring_match(self):
        result = SimilarityEngine.calculate_jaccard(
            ["wordpress", "ethical hacking"],
            ["wordpress development", "ethical hacking course"],
        )
        assert result["matched_count"] == 2
        assert result["missing_skills"] == []

    def test_fuzzy_similarity_match(self):
        result = SimilarityEngine.calculate_jaccard(
            ["node js", "react.js"],
            ["node.js", "reactjs"],
        )
        assert result["matched_count"] == 2
        assert result["missing_skills"] == []

    def test_fuzzy_does_not_false_positive(self):
        result = SimilarityEngine.calculate_jaccard(
            ["java"], ["javascript"]
        )
        assert result["matched_count"] == 0
        assert result["missing_skills"] == ["javascript"]

    def test_fuzzy_with_exact_and_partial(self):
        result = SimilarityEngine.calculate_jaccard(
            ["python", "docker", "fastapi"],
            ["python", "fastapi framework", "kubernetes"],
        )
        assert "python" in result["matched_skills"]
        assert "kubernetes" in result["missing_skills"]
        assert result["matched_count"] == 2


class TestScoreCalibration:

    def test_midpoint_is_fifty(self):
        result = SimilarityEngine.calibrate_score(K_SIGMOID_MIDPOINT)
        assert result == 50.0

    def test_high_raw_gives_near_hundred(self):
        result = SimilarityEngine.calibrate_score(0.9)
        assert result > 95.0

    def test_low_raw_gives_near_zero(self):
        result = SimilarityEngine.calibrate_score(0.05)
        assert result < 5.0

    def test_clamped_to_zero_hundred(self):
        assert SimilarityEngine.calibrate_score(-1.0) >= 0.0
        assert SimilarityEngine.calibrate_score(2.0) <= 100.0

    def test_monotonically_increasing(self):
        scores = [SimilarityEngine.calibrate_score(x / 10.0) for x in range(11)]
        for i in range(1, len(scores)):
            assert scores[i] >= scores[i - 1]

    def test_spreads_middle_range(self):
        low = SimilarityEngine.calibrate_score(0.3)
        high = SimilarityEngine.calibrate_score(0.6)
        assert high - low > 50


class TestScoreBands:

    def test_excellent(self):
        band = SimilarityEngine.get_score_band(95.0)
        assert band["rating"] == "Excellent Match"

    def test_good(self):
        band = SimilarityEngine.get_score_band(80.0)
        assert band["rating"] == "Good Match"

    def test_moderate(self):
        band = SimilarityEngine.get_score_band(65.0)
        assert band["rating"] == "Moderate Match"

    def test_weak(self):
        band = SimilarityEngine.get_score_band(50.0)
        assert band["rating"] == "Weak Match"

    def test_poor(self):
        band = SimilarityEngine.get_score_band(20.0)
        assert band["rating"] == "Poor Match"

    def test_boundary_ninety(self):
        band = SimilarityEngine.get_score_band(90.0)
        assert band["rating"] == "Excellent Match"

    def test_boundary_zero(self):
        band = SimilarityEngine.get_score_band(0.0)
        assert band["rating"] == "Poor Match"

    def test_float_between_bands(self):
        band = SimilarityEngine.get_score_band(89.5)
        assert band["rating"] == "Good Match"

    def test_exact_hundred(self):
        band = SimilarityEngine.get_score_band(100.0)
        assert band["rating"] == "Excellent Match"


def _make_vectors(cv_skills, jd_skills, embedding_val=0.5):
    """Helper to build minimal cv_vectors / jd_vectors for testing."""
    dim = 4
    emb = [embedding_val] * dim
    cv_vectors = {
        "section_embeddings": {
            "overall": emb,
            "skills": emb,
            "experience": emb,
            "education": emb,
        },
        "skills_list": cv_skills,
        "raw_text": "test cv text",
        "_fallback": False,
    }
    jd_vectors = {
        "section_embeddings": {
            "overall": emb,
            "skills": emb,
        },
        "skills_list": jd_skills,
        "cleaned_text": "test jd text",
    }
    return cv_vectors, jd_vectors


class TestCalculateMatchFull:

    def test_returns_all_report_fields(self):
        engine = SimilarityEngine()
        cv_v, jd_v = _make_vectors(K_CV_SKILLS, K_JD_SKILLS)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.5)

        assert "match_percentage" in result
        assert "match_rating" in result
        assert "recommendation" in result
        assert "confidence" in result
        assert "breakdown" in result
        assert "skill_details" in result
        assert "strengths" in result
        assert "gaps" in result

    def test_percentage_in_range(self):
        engine = SimilarityEngine()
        cv_v, jd_v = _make_vectors(K_CV_SKILLS, K_JD_SKILLS)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.5)
        assert 0 <= result["match_percentage"] <= 100

    def test_perfect_match_high_score(self):
        engine = SimilarityEngine()
        skills = ["python", "react", "docker"]
        cv_v, jd_v = _make_vectors(skills, skills, embedding_val=0.9)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.9)
        assert result["match_percentage"] > 80

    def test_weights_sum_to_one(self):
        assert abs(sum(K_WEIGHTS_FULL.values()) - 1.0) < 1e-9
        assert abs(sum(K_WEIGHTS_FALLBACK.values()) - 1.0) < 1e-9

    def test_skill_details_present(self):
        engine = SimilarityEngine()
        cv_v, jd_v = _make_vectors(K_CV_SKILLS, K_JD_SKILLS)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.5)
        assert result["skill_details"] is not None
        assert "matched_skills" in result["skill_details"]

    def test_breakdown_has_skills_section(self):
        engine = SimilarityEngine()
        cv_v, jd_v = _make_vectors(K_CV_SKILLS, K_JD_SKILLS)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.5)
        assert "skills" in result["breakdown"]
        assert "matched" in result["breakdown"]["skills"]

    def test_strengths_populated_when_skills_match(self):
        engine = SimilarityEngine()
        cv_v, jd_v = _make_vectors(K_CV_SKILLS, K_JD_SKILLS)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.5)
        assert len(result["strengths"]) > 0

    def test_gaps_populated_when_skills_missing(self):
        engine = SimilarityEngine()
        cv_v, jd_v = _make_vectors(K_CV_SKILLS, K_JD_SKILLS)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.5)
        assert any("Missing" in g for g in result["gaps"])

    def test_confidence_high_in_full_mode(self):
        engine = SimilarityEngine()
        cv_v, jd_v = _make_vectors(K_CV_SKILLS, K_JD_SKILLS)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.5)
        assert result["confidence"] == "high"

    def test_not_fallback(self):
        engine = SimilarityEngine()
        cv_v, jd_v = _make_vectors(K_CV_SKILLS, K_JD_SKILLS)
        result = engine.calculate_match(cv_v, jd_v, tfidf_sim=0.5)
        assert result["_fallback"] is False


class TestCalculateMatchFallback:

    def test_fallback_has_no_skill_details(self):
        engine = SimilarityEngine()
        cv_vectors = {
            "section_embeddings": {"overall": [0.5, 0.5, 0.5, 0.5]},
            "skills_list": [],
            "raw_text": "raw cv text",
            "_fallback": True,
        }
        jd_vectors = {
            "section_embeddings": {"overall": [0.5, 0.5, 0.5, 0.5]},
            "skills_list": ["python"],
            "cleaned_text": "jd text",
        }
        result = engine.calculate_match(cv_vectors, jd_vectors, tfidf_sim=0.3, is_fallback=True)
        assert result["skill_details"] is None
        assert result["confidence"] == "reduced"
        assert result["_fallback"] is True

    def test_fallback_percentage_in_range(self):
        engine = SimilarityEngine()
        cv_vectors = {
            "section_embeddings": {"overall": [0.1, 0.2]},
            "skills_list": [],
            "raw_text": "",
            "_fallback": True,
        }
        jd_vectors = {
            "section_embeddings": {"overall": [0.3, 0.4]},
            "skills_list": [],
            "cleaned_text": "",
        }
        result = engine.calculate_match(cv_vectors, jd_vectors, tfidf_sim=0.2, is_fallback=True)
        assert 0 <= result["match_percentage"] <= 100

    def test_fallback_uses_fallback_weights(self):
        engine = SimilarityEngine()
        cv_vectors = {
            "section_embeddings": {"overall": [0.5, 0.5]},
            "skills_list": [],
            "raw_text": "",
            "_fallback": True,
        }
        jd_vectors = {
            "section_embeddings": {"overall": [0.5, 0.5]},
            "skills_list": [],
            "cleaned_text": "",
        }
        result = engine.calculate_match(cv_vectors, jd_vectors, tfidf_sim=0.5, is_fallback=True)
        assert result["weights_used"] == K_WEIGHTS_FALLBACK
