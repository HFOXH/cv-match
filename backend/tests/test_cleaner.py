from nlp_preprocessing.cleaner import TextCleaner


class TestCleanText:
    """Tests for TextCleaner.clean_text()."""

    def test_removes_urls(self):
        text = "Visit https://example.com for details"
        result = TextCleaner.clean_text(text)
        assert "https://example.com" not in result
        assert "Visit" in result

    def test_removes_www_urls(self):
        text = "Go to www.example.com for info"
        result = TextCleaner.clean_text(text)
        assert "www.example.com" not in result

    def test_removes_emails(self):
        text = "Contact us at hr@company.com for applications"
        result = TextCleaner.clean_text(text)
        assert "hr@company.com" not in result
        assert "Contact" in result

    def test_removes_non_ascii(self):
        text = "Developer with experience in résumé building"
        result = TextCleaner.clean_text(text)
        assert "é" not in result

    def test_normalizes_whitespace(self):
        text = "Python   developer  with   experience"
        result = TextCleaner.clean_text(text)
        assert "   " not in result
        assert result == "Python developer with experience"

    def test_strips_leading_trailing_whitespace(self):
        text = "   Python developer   "
        result = TextCleaner.clean_text(text)
        assert result == "Python developer"

    def test_empty_string(self):
        assert TextCleaner.clean_text("") == ""

    def test_none_input(self):
        assert TextCleaner.clean_text(None) == ""

    def test_preserves_normal_text(self):
        text = "Senior Python Developer with 5 years experience"
        result = TextCleaner.clean_text(text)
        assert result == text


class TestRemoveUrls:
    """Tests for TextCleaner.remove_urls()."""

    def test_removes_http_url(self):
        assert "http" not in TextCleaner.remove_urls("Visit http://example.com")

    def test_removes_https_url(self):
        assert "https" not in TextCleaner.remove_urls("Visit https://example.com/path")


class TestRemoveEmails:
    """Tests for TextCleaner.remove_emails()."""

    def test_removes_email(self):
        result = TextCleaner.remove_emails("Email john@company.com for details")
        assert "john@company.com" not in result


class TestNormalizeWhitespace:
    """Tests for TextCleaner.normalize_whitespace()."""

    def test_collapses_spaces(self):
        assert TextCleaner.normalize_whitespace("a   b") == "a b"

    def test_collapses_tabs_and_newlines(self):
        assert TextCleaner.normalize_whitespace("a\t\n\nb") == "a b"


class TestNormalizeSkills:
    """Tests for TextCleaner.normalize_skills()."""

    def test_lowercases_skills(self):
        result = TextCleaner.normalize_skills(["Python", "JavaScript", "AWS"])
        assert result == ["python", "javascript", "aws"]

    def test_removes_duplicates(self):
        result = TextCleaner.normalize_skills(["Python", "python", "PYTHON"])
        assert result == ["python"]

    def test_strips_whitespace(self):
        result = TextCleaner.normalize_skills(["  Python ", "JavaScript  "])
        assert result == ["python", "javascript"]

    def test_filters_empty_strings(self):
        result = TextCleaner.normalize_skills(["Python", "", "  ", "AWS"])
        assert result == ["python", "aws"]

    def test_preserves_order(self):
        result = TextCleaner.normalize_skills(["Docker", "AWS", "Python"])
        assert result == ["docker", "aws", "python"]

    def test_empty_list(self):
        assert TextCleaner.normalize_skills([]) == []

    def test_mixed_case_duplicates(self):
        result = TextCleaner.normalize_skills(["React", "react.js", "REACT", "React"])
        assert result == ["react", "react.js"]
