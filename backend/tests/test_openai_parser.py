import json
import os
import pytest
from unittest.mock import patch, MagicMock

from cv_processor.parsers.openai_parser import OpenAICVParser, get_parser, fallback_parse
from cv_processor import CVProcessor
from cv_processor.exceptions import ParsingError, ProcessingError


K_SAMPLE_CV_TEXT = """\
Santiago Cardenas
santiago@example.com
+1 (555) 123-4567
Toronto, ON

SKILLS
Python, JavaScript, React, FastAPI, Machine Learning

EXPERIENCE
Senior Developer at Tech Corp
January 2020 - Present
- Led development of NLP pipeline

EDUCATION
Bachelor of Science in Computer Science
University of Technology, 2018
"""

K_MOCK_OPENAI_RESPONSE = {
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
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University of Technology",
            "year": "2018",
            "field": "Computer Science",
        }
    ],
    "certifications": [],
    "summary": None,
}


# /*
# * function name: _mock_completion()
# * Description: Helper to create a mock OpenAI ChatCompletion response object.
# * Parameter: content : str : The JSON string the mock API should return.
# * return: MagicMock : Mock response object with choices[0].message.content set.
# */
def _mock_completion(content: str):
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


class TestOpenAICVParser:
    """Tests for the OpenAICVParser class."""

    @patch("cv_processor.parsers.openai_parser.OpenAI")
    def test_successful_parse(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps(K_MOCK_OPENAI_RESPONSE)
        )

        parser = OpenAICVParser(api_key="test-key")
        result = parser.parse_cv(K_SAMPLE_CV_TEXT)

        assert result["contact"]["name"] == "Santiago Cardenas"
        assert result["contact"]["email"] == "santiago@example.com"
        assert "Python" in result["skills"]
        assert len(result["experience"]) == 1
        assert result["experience"][0]["job_title"] == "Senior Developer"
        assert len(result["education"]) == 1
        assert result["certifications"] == []

    @patch("cv_processor.parsers.openai_parser.OpenAI")
    def test_api_error_raises_parsing_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        parser = OpenAICVParser(api_key="test-key")
        with pytest.raises(ParsingError):
            parser.parse_cv(K_SAMPLE_CV_TEXT)

    @patch("cv_processor.parsers.openai_parser.OpenAI")
    def test_invalid_json_raises_parsing_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            "This is not valid JSON"
        )

        parser = OpenAICVParser(api_key="test-key")
        with pytest.raises(ParsingError):
            parser.parse_cv(K_SAMPLE_CV_TEXT)

    @patch("cv_processor.parsers.openai_parser.OpenAI")
    def test_validate_output_adds_missing_keys(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps({"contact": {"name": "Test"}, "skills": ["Python"]})
        )

        parser = OpenAICVParser(api_key="test-key")
        result = parser.parse_cv(K_SAMPLE_CV_TEXT)

        assert "experience" in result
        assert "education" in result
        assert "certifications" in result
        assert "summary" in result
        assert result["skills"] == ["Python"]


class TestGetParser:
    """Tests for get_parser factory function."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_returns_parser_when_key_set(self):
        parser = get_parser()
        assert parser is not None
        assert isinstance(parser, OpenAICVParser)

    @patch.dict(os.environ, {}, clear=True)
    def test_returns_none_when_key_missing(self):
        os.environ.pop("OPENAI_API_KEY", None)
        parser = get_parser()
        assert parser is None


class TestFallbackParse:
    """Tests for fallback_parse function."""

    def test_fallback_structure(self):
        result = fallback_parse("some text")

        assert result["contact"]["name"] is None
        assert result["contact"]["email"] is None
        assert result["skills"] == []
        assert result["experience"] == []
        assert result["education"] == []
        assert result["certifications"] == []
        assert result["summary"] is None
        assert result["_fallback"] is True


class TestCVProcessor:
    """Tests for the CVProcessor orchestrator."""

    @patch.dict(os.environ, {}, clear=True)
    def test_process_text_fallback_when_no_key(self):
        os.environ.pop("OPENAI_API_KEY", None)

        result = CVProcessor.process_text(K_SAMPLE_CV_TEXT)

        assert result["raw_text"] == K_SAMPLE_CV_TEXT
        assert result["parsing_method"] == "fallback"
        assert result["parsed_data"]["_fallback"] is True
        assert result["metadata"]["text_length"] == len(K_SAMPLE_CV_TEXT)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("cv_processor.parsers.openai_parser.OpenAI")
    def test_process_text_openai_success(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = _mock_completion(
            json.dumps(K_MOCK_OPENAI_RESPONSE)
        )

        result = CVProcessor.process_text(K_SAMPLE_CV_TEXT)

        assert result["parsing_method"] == "openai"
        assert result["parsed_data"]["contact"]["name"] == "Santiago Cardenas"
        assert result["metadata"]["skills_count"] == 5

    def test_process_text_empty_raises_error(self):
        with pytest.raises(ProcessingError):
            CVProcessor.process_text("")

    def test_process_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            CVProcessor.process_file("nonexistent.pdf")

    def test_process_file_unsupported_format(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            tmp_path = f.name
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                CVProcessor.process_file(tmp_path)
        finally:
            os.unlink(tmp_path)
