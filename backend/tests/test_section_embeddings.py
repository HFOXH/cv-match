from unittest.mock import MagicMock

from embedding.section_embeddings import SectionEmbeddingGenerator


def _make_mock_encoder(batch_results):
    """Create a mock encoder that returns given batch results."""
    encoder = MagicMock()
    encoder.encode_batch.return_value = batch_results
    return encoder


class TestCVSectionEmbeddings:
    """Tests for CV section embedding generation."""

    def test_all_sections_populated(self):
        mock_encoder = _make_mock_encoder([[0.1], [0.2], [0.3], [0.4]])

        generator = SectionEmbeddingGenerator(mock_encoder)
        result = generator.generate_cv_section_embeddings({
            "skills": ["python", "react"],
            "experience_text": "3 years at Google",
            "education_text": "BSc from MIT",
            "full_text_for_embedding": "Full profile summary",
        })

        assert result["skills"] == [0.1]
        assert result["experience"] == [0.2]
        assert result["education"] == [0.3]
        assert result["overall"] == [0.4]
        mock_encoder.encode_batch.assert_called_once()

    def test_missing_education(self):
        mock_encoder = _make_mock_encoder([[0.1], [0.2], [0.3]])

        generator = SectionEmbeddingGenerator(mock_encoder)
        result = generator.generate_cv_section_embeddings({
            "skills": ["python"],
            "experience_text": "3 years at Google",
            "education_text": "",  # empty
            "full_text_for_embedding": "Full profile summary",
        })

        assert result["skills"] == [0.1]
        assert result["experience"] == [0.2]
        assert result["education"] is None  # not embedded
        assert result["overall"] == [0.3]

    def test_empty_normalization(self):
        mock_encoder = MagicMock()

        generator = SectionEmbeddingGenerator(mock_encoder)
        result = generator.generate_cv_section_embeddings({
            "skills": [],
            "experience_text": "",
            "education_text": "",
            "full_text_for_embedding": "",
        })

        assert result["skills"] is None
        assert result["experience"] is None
        assert result["education"] is None
        assert result["overall"] is None
        mock_encoder.encode_batch.assert_not_called()

    def test_skills_joined_as_comma_string(self):
        mock_encoder = _make_mock_encoder([[0.1], [0.2]])

        generator = SectionEmbeddingGenerator(mock_encoder)
        generator.generate_cv_section_embeddings({
            "skills": ["python", "react", "docker"],
            "experience_text": "",
            "education_text": "",
            "full_text_for_embedding": "Summary",
        })

        call_args = mock_encoder.encode_batch.call_args[0][0]
        assert call_args[0] == "python, react, docker"


class TestJDSectionEmbeddings:
    """Tests for JD section embedding generation."""

    def test_jd_with_skills_and_text(self):
        mock_encoder = _make_mock_encoder([[0.1], [0.2]])

        generator = SectionEmbeddingGenerator(mock_encoder)
        result = generator.generate_jd_section_embeddings({
            "required_skills": ["python", "aws"],
            "preferred_skills": ["docker"],
            "cleaned_text": "Looking for a Python engineer",
        })

        assert result["skills"] == [0.1]
        assert result["overall"] == [0.2]

    def test_jd_no_skills(self):
        mock_encoder = _make_mock_encoder([[0.1]])

        generator = SectionEmbeddingGenerator(mock_encoder)
        result = generator.generate_jd_section_embeddings({
            "required_skills": [],
            "preferred_skills": [],
            "cleaned_text": "Looking for an engineer",
        })

        assert result["skills"] is None
        assert result["overall"] == [0.1]

    def test_jd_combines_required_and_preferred_skills(self):
        mock_encoder = _make_mock_encoder([[0.1], [0.2]])

        generator = SectionEmbeddingGenerator(mock_encoder)
        generator.generate_jd_section_embeddings({
            "required_skills": ["python", "aws"],
            "preferred_skills": ["docker", "kubernetes"],
            "cleaned_text": "Job description text",
        })

        call_args = mock_encoder.encode_batch.call_args[0][0]
        assert call_args[0] == "python, aws, docker, kubernetes"

    def test_jd_empty(self):
        mock_encoder = MagicMock()

        generator = SectionEmbeddingGenerator(mock_encoder)
        result = generator.generate_jd_section_embeddings({
            "required_skills": [],
            "preferred_skills": [],
            "cleaned_text": "",
        })

        assert result["skills"] is None
        assert result["overall"] is None
        mock_encoder.encode_batch.assert_not_called()
