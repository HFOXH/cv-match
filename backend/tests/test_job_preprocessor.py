import json
import logging
from unittest.mock import patch, MagicMock

from nlp_preprocessing.job_preprocessor import JobDescriptionPreprocessor


K_SAMPLE_JOB_DESCRIPTION = """\
Senior Python Developer

We are looking for an experienced Python developer to join our engineering team.

Requirements:
- 5+ years of experience with Python
- Strong knowledge of FastAPI or Django
- Experience with PostgreSQL and Redis
- Familiarity with Docker and Kubernetes
- Understanding of Machine Learning concepts

Nice to have:
- Experience with React or Angular
- AWS certification
- Knowledge of CI/CD pipelines

Bachelor's degree in Computer Science or equivalent experience.
"""

K_MOCK_OPENAI_EXTRACTION = {
    "required_skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis",
                        "Docker", "Kubernetes", "Machine Learning"],
    "preferred_skills": ["React", "Angular", "AWS", "CI/CD"],
    "experience_years": "5+ years",
    "education_level": "Bachelor's",
    "key_phrases": ["python developer", "engineering team", "machine learning"],
}


def _mock_completion(content: str):
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


class TestJobDescriptionPreprocessor:
    """Tests for JobDescriptionPreprocessor."""

    @patch("nlp_preprocessing.job_preprocessor.OpenAI")
    def test_preprocess_returns_all_fields(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps(K_MOCK_OPENAI_EXTRACTION)
        )

        preprocessor = JobDescriptionPreprocessor(openai_api_key="test-key")
        result = preprocessor.preprocess(K_SAMPLE_JOB_DESCRIPTION)

        assert "original_text" in result
        assert "cleaned_text" in result
        assert "tokens" in result
        assert "lemmas" in result
        assert "key_phrases" in result
        assert "required_skills" in result
        assert "preferred_skills" in result
        assert "experience_years" in result
        assert "education_level" in result

    @patch("nlp_preprocessing.job_preprocessor.OpenAI")
    def test_preprocess_openai_extraction(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps(K_MOCK_OPENAI_EXTRACTION)
        )

        preprocessor = JobDescriptionPreprocessor(openai_api_key="test-key")
        result = preprocessor.preprocess(K_SAMPLE_JOB_DESCRIPTION)

        assert "python" in result["required_skills"]
        assert "react" in result["preferred_skills"]
        assert result["experience_years"] == "5+ years"
        assert result["education_level"] == "Bachelor's"

    def test_preprocess_empty_text(self):
        preprocessor = JobDescriptionPreprocessor(openai_api_key=None)
        result = preprocessor.preprocess("")

        assert result["original_text"] == ""
        assert result["cleaned_text"] == ""
        assert result["tokens"] == []
        assert result["lemmas"] == []
        assert result["required_skills"] == []

    def test_preprocess_none_text(self):
        preprocessor = JobDescriptionPreprocessor(openai_api_key=None)
        result = preprocessor.preprocess(None)

        assert result["tokens"] == []

    def test_clean_text(self):
        preprocessor = JobDescriptionPreprocessor(openai_api_key=None)
        text = "Visit https://example.com and email hr@company.com"
        cleaned = preprocessor.clean_text(text)

        assert "https://example.com" not in cleaned
        assert "hr@company.com" not in cleaned

    def test_tokenize_produces_tokens(self):
        preprocessor = JobDescriptionPreprocessor(openai_api_key=None)
        tokens = preprocessor.tokenize("Python developer with experience")

        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert "Python" in tokens

    def test_tokenize_removes_stop_words(self):
        preprocessor = JobDescriptionPreprocessor(openai_api_key=None)
        tokens = preprocessor.tokenize("The developer should include Python")

        token_lower = [t.lower() for t in tokens]
        assert "the" not in token_lower
        assert "should" not in token_lower

    def test_lemmatize_produces_lemmas(self):
        preprocessor = JobDescriptionPreprocessor(openai_api_key=None)
        lemmas = preprocessor.lemmatize(["developing", "applications"])

        assert isinstance(lemmas, list)
        assert len(lemmas) > 0


class TestErrorHandling:
    """Tests for error logging when OpenAI fails."""

    @patch("nlp_preprocessing.job_preprocessor.OpenAI")
    def test_returns_empty_on_api_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        preprocessor = JobDescriptionPreprocessor(openai_api_key="test-key")
        result = preprocessor.openai_extract(K_SAMPLE_JOB_DESCRIPTION)

        assert result["required_skills"] == []
        assert result["preferred_skills"] == []
        assert result["experience_years"] is None
        assert result["education_level"] is None

    @patch("nlp_preprocessing.job_preprocessor.OpenAI")
    def test_returns_empty_on_invalid_json(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            "This is not valid JSON"
        )

        preprocessor = JobDescriptionPreprocessor(openai_api_key="test-key")
        result = preprocessor.openai_extract(K_SAMPLE_JOB_DESCRIPTION)

        assert result["required_skills"] == []

    @patch.dict("os.environ", {}, clear=True)
    def test_returns_empty_when_no_client(self):
        preprocessor = JobDescriptionPreprocessor(openai_api_key=None)
        result = preprocessor.openai_extract("Some job description")

        assert result["required_skills"] == []
        assert result["preferred_skills"] == []

    @patch("nlp_preprocessing.job_preprocessor.OpenAI")
    def test_logs_error_on_api_failure(self, mock_openai_cls, caplog):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Connection timeout")

        preprocessor = JobDescriptionPreprocessor(openai_api_key="test-key")

        with caplog.at_level(logging.ERROR):
            preprocessor.openai_extract(K_SAMPLE_JOB_DESCRIPTION)

        assert "OpenAI API call failed" in caplog.text

    @patch("nlp_preprocessing.job_preprocessor.OpenAI")
    def test_logs_error_on_json_parse_failure(self, mock_openai_cls, caplog):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            "not json {{"
        )

        preprocessor = JobDescriptionPreprocessor(openai_api_key="test-key")

        with caplog.at_level(logging.ERROR):
            preprocessor.openai_extract(K_SAMPLE_JOB_DESCRIPTION)

        assert "Failed to parse OpenAI response as JSON" in caplog.text

    @patch.dict("os.environ", {}, clear=True)
    def test_logs_error_when_no_api_key(self, caplog):
        with caplog.at_level(logging.ERROR):
            JobDescriptionPreprocessor(openai_api_key=None)

        assert "No OpenAI API key provided" in caplog.text


class TestOpenAIExtraction:
    """Tests for successful OpenAI extraction."""

    @patch("nlp_preprocessing.job_preprocessor.OpenAI")
    def test_openai_extract_success(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps(K_MOCK_OPENAI_EXTRACTION)
        )

        preprocessor = JobDescriptionPreprocessor(openai_api_key="test-key")
        result = preprocessor.openai_extract(K_SAMPLE_JOB_DESCRIPTION)

        assert "Python" in result["required_skills"]
        assert "React" in result["preferred_skills"]
