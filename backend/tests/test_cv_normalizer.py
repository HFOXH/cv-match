import json
import logging
from unittest.mock import patch, MagicMock

from nlp_preprocessing.cv_normalizer import CVDataNormalizer


K_SAMPLE_PARSED_CV = {
    "contact": {
        "name": "Santiago Cardenas",
        "email": "santiago@example.com",
        "phone": "+1 (555) 123-4567",
        "location": "Toronto, ON",
        "linkedin": None,
    },
    "skills": ["Python", "JavaScript", "React", "FastAPI", "Machine Learning"],
    "experience": [
        {
            "job_title": "Senior Developer",
            "company": "Tech Corp",
            "start_date": "January 2020",
            "end_date": "Present",
            "description": "Led development of NLP pipeline",
        }
    ],
    "education": [
        {
            "degree": "Bachelor of Science",
            "institution": "University of Toronto",
            "year": "2020",
            "field": "Computer Science",
        }
    ],
    "certifications": ["AWS Cloud Practitioner"],
    "summary": "Experienced software engineer specializing in NLP",
}

K_MOCK_OPENAI_NORMALIZATION = {
    "skills": ["python", "javascript", "react", "fastapi", "machine learning"],
    "experience_text": "Senior Developer at Tech Corp. Led development of NLP pipeline.",
    "education_text": "Bachelor of Science in Computer Science from University of Toronto.",
    "full_text_for_embedding": (
        "Experienced software engineer specializing in NLP. "
        "Skilled in Python, JavaScript, React, FastAPI, and Machine Learning. "
        "Senior Developer at Tech Corp where he led development of NLP pipeline. "
        "Bachelor of Science in Computer Science from University of Toronto. "
        "AWS Cloud Practitioner certified."
    ),
}


def _mock_completion(content: str):
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


class TestNormalizeWithOpenAI:
    """Tests for OpenAI-powered normalization."""

    @patch("nlp_preprocessing.cv_normalizer.OpenAI")
    def test_normalize_returns_all_fields(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps(K_MOCK_OPENAI_NORMALIZATION)
        )

        normalizer = CVDataNormalizer(openai_api_key="test-key")
        result = normalizer.normalize(K_SAMPLE_PARSED_CV)

        assert "skills" in result
        assert "experience_text" in result
        assert "education_text" in result
        assert "full_text_for_embedding" in result

    @patch("nlp_preprocessing.cv_normalizer.OpenAI")
    def test_normalize_skills_from_openai(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps(K_MOCK_OPENAI_NORMALIZATION)
        )

        normalizer = CVDataNormalizer(openai_api_key="test-key")
        result = normalizer.normalize(K_SAMPLE_PARSED_CV)

        assert "python" in result["skills"]
        assert "javascript" in result["skills"]
        assert "machine learning" in result["skills"]

    @patch("nlp_preprocessing.cv_normalizer.OpenAI")
    def test_normalize_embedding_text_from_openai(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps(K_MOCK_OPENAI_NORMALIZATION)
        )

        normalizer = CVDataNormalizer(openai_api_key="test-key")
        result = normalizer.normalize(K_SAMPLE_PARSED_CV)

        assert "NLP" in result["full_text_for_embedding"]
        assert "Tech Corp" in result["experience_text"]


class TestErrorHandling:
    """Tests for error logging when OpenAI fails."""

    @patch("nlp_preprocessing.cv_normalizer.OpenAI")
    def test_returns_empty_on_api_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        normalizer = CVDataNormalizer(openai_api_key="test-key")
        result = normalizer.normalize(K_SAMPLE_PARSED_CV)

        assert result["skills"] == []
        assert result["experience_text"] == ""
        assert result["education_text"] == ""
        assert result["full_text_for_embedding"] == ""

    @patch("nlp_preprocessing.cv_normalizer.OpenAI")
    def test_returns_empty_on_invalid_json(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            "This is not valid JSON"
        )

        normalizer = CVDataNormalizer(openai_api_key="test-key")
        result = normalizer.normalize(K_SAMPLE_PARSED_CV)

        assert result["skills"] == []
        assert result["experience_text"] == ""

    @patch.dict("os.environ", {}, clear=True)
    def test_returns_empty_when_no_client(self):
        normalizer = CVDataNormalizer(openai_api_key=None)
        result = normalizer.normalize(K_SAMPLE_PARSED_CV)

        assert result["skills"] == []
        assert result["experience_text"] == ""
        assert result["education_text"] == ""
        assert result["full_text_for_embedding"] == ""

    @patch("nlp_preprocessing.cv_normalizer.OpenAI")
    def test_logs_error_on_api_failure(self, mock_openai_cls, caplog):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Connection timeout")

        normalizer = CVDataNormalizer(openai_api_key="test-key")

        with caplog.at_level(logging.ERROR):
            normalizer.normalize(K_SAMPLE_PARSED_CV)

        assert "OpenAI API call failed" in caplog.text

    @patch.dict("os.environ", {}, clear=True)
    def test_logs_error_when_no_api_key(self, caplog):
        with caplog.at_level(logging.ERROR):
            CVDataNormalizer(openai_api_key=None)

        assert "No OpenAI API key provided" in caplog.text
