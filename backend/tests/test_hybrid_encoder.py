import os
import tempfile
from unittest.mock import patch, MagicMock

from embedding.hybrid_encoder import HybridEncoder


K_SAMPLE_NORMALIZED_CV = {
    "skills": ["python", "react", "docker"],
    "experience_text": "Senior Developer at Tech Corp for 3 years",
    "education_text": "BSc Computer Science from MIT",
    "full_text_for_embedding": "Experienced Python developer with React and Docker skills",
}

K_SAMPLE_PREPROCESSED_JD = {
    "required_skills": ["python", "aws"],
    "preferred_skills": ["docker"],
    "cleaned_text": "Looking for a Python engineer with AWS experience",
}

K_MOCK_CV_EMBEDDINGS = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]]
K_MOCK_JD_EMBEDDINGS = [[0.2, 0.3], [0.4, 0.5]]


def _make_encoder(mock_encoder_cls, encode_return=None, encode_batch_return=None):
    """Set up mock OpenAI encoder and return a HybridEncoder with temp DB."""
    mock_encoder = MagicMock()
    mock_encoder_cls.return_value = mock_encoder
    if encode_return is not None:
        mock_encoder.encode.return_value = encode_return
    if encode_batch_return is not None:
        mock_encoder.encode_batch.return_value = encode_batch_return

    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    encoder = HybridEncoder(db_path=tmp.name)
    return encoder, tmp.name


class TestEncodeCVNormalMode:
    """Tests for CV encoding in normal mode."""

    @patch("embedding.hybrid_encoder.OpenAIEncoder")
    def test_encode_cv_returns_all_fields(self, mock_encoder_cls):
        encoder, db_path = _make_encoder(mock_encoder_cls, encode_batch_return=K_MOCK_CV_EMBEDDINGS)
        try:
            result = encoder.encode_cv(
                cv_id="test-123",
                normalized_cv=K_SAMPLE_NORMALIZED_CV,
                raw_text="Raw CV text here",
                parsing_method="openai",
            )

            assert result["cv_id"] == "test-123"
            assert result["_fallback"] is False
            assert result["skills_list"] == ["python", "react", "docker"]
            assert result["section_embeddings"]["skills"] is not None
            assert result["section_embeddings"]["experience"] is not None
            assert result["section_embeddings"]["education"] is not None
            assert result["section_embeddings"]["overall"] is not None
        finally:
            encoder.vector_store.close()
            os.unlink(db_path)

    @patch("embedding.hybrid_encoder.OpenAIEncoder")
    def test_encode_cv_saves_to_cache(self, mock_encoder_cls):
        encoder, db_path = _make_encoder(mock_encoder_cls, encode_batch_return=K_MOCK_CV_EMBEDDINGS)
        try:
            encoder.encode_cv(
                cv_id="test-123",
                normalized_cv=K_SAMPLE_NORMALIZED_CV,
                raw_text="Raw CV text",
            )

            cached = encoder.vector_store.get_cv_vectors("test-123")
            assert cached is not None
            assert cached["skills_list"] == ["python", "react", "docker"]
        finally:
            encoder.vector_store.close()
            os.unlink(db_path)

    @patch("embedding.hybrid_encoder.OpenAIEncoder")
    def test_encode_cv_uses_cache_on_second_call(self, mock_encoder_cls):
        mock_encoder = MagicMock()
        mock_encoder_cls.return_value = mock_encoder
        mock_encoder.encode_batch.return_value = K_MOCK_CV_EMBEDDINGS

        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        try:
            encoder = HybridEncoder(db_path=tmp.name)

            # First call - generates embeddings
            encoder.encode_cv(
                cv_id="test-123",
                normalized_cv=K_SAMPLE_NORMALIZED_CV,
                raw_text="Raw CV text",
            )

            # Second call - should use cache
            result = encoder.encode_cv(
                cv_id="test-123",
                normalized_cv=K_SAMPLE_NORMALIZED_CV,
                raw_text="Raw CV text",
            )

            # encode_batch should only be called once (first call)
            assert mock_encoder.encode_batch.call_count == 1
            assert result["cv_id"] == "test-123"
        finally:
            encoder.vector_store.close()
            os.unlink(tmp.name)


class TestEncodeCVFallbackMode:
    """Tests for CV encoding in fallback mode."""

    @patch("embedding.hybrid_encoder.OpenAIEncoder")
    def test_fallback_when_parsing_method_is_fallback(self, mock_encoder_cls):
        encoder, db_path = _make_encoder(mock_encoder_cls, encode_return=[0.1, 0.2])
        try:
            result = encoder.encode_cv(
                cv_id="test-123",
                normalized_cv=K_SAMPLE_NORMALIZED_CV,
                raw_text="Raw CV text",
                parsing_method="fallback",
            )

            assert result["_fallback"] is True
            assert result["section_embeddings"]["overall"] == [0.1, 0.2]
            assert result["section_embeddings"]["skills"] is None
            assert result["section_embeddings"]["experience"] is None
            assert result["section_embeddings"]["education"] is None
            assert result["skills_list"] == []
        finally:
            encoder.vector_store.close()
            os.unlink(db_path)

    @patch("embedding.hybrid_encoder.OpenAIEncoder")
    def test_fallback_when_normalization_empty(self, mock_encoder_cls):
        encoder, db_path = _make_encoder(mock_encoder_cls, encode_return=[0.5, 0.6])
        try:
            result = encoder.encode_cv(
                cv_id="test-123",
                normalized_cv={"skills": [], "experience_text": "",
                               "education_text": "", "full_text_for_embedding": ""},
                raw_text="Raw CV text",
                parsing_method="openai",
            )

            assert result["_fallback"] is True
        finally:
            encoder.vector_store.close()
            os.unlink(db_path)


class TestEncodeJD:
    """Tests for job description encoding."""

    @patch("embedding.hybrid_encoder.OpenAIEncoder")
    def test_encode_jd_returns_expected_structure(self, mock_encoder_cls):
        encoder, db_path = _make_encoder(mock_encoder_cls, encode_batch_return=K_MOCK_JD_EMBEDDINGS)
        try:
            result = encoder.encode_job_description(K_SAMPLE_PREPROCESSED_JD)

            assert result["section_embeddings"]["skills"] is not None
            assert result["section_embeddings"]["overall"] is not None
            assert result["skills_list"] == ["python", "aws", "docker"]
            assert result["cleaned_text"] == K_SAMPLE_PREPROCESSED_JD["cleaned_text"]
        finally:
            encoder.vector_store.close()
            os.unlink(db_path)


class TestTFIDFVectors:
    """Tests for TF-IDF computation."""

    @patch("embedding.hybrid_encoder.OpenAIEncoder")
    def test_compute_tfidf_vectors(self, mock_encoder_cls):
        encoder, db_path = _make_encoder(mock_encoder_cls)
        try:
            result = encoder.compute_tfidf_vectors(
                "Python developer with Docker experience",
                "Looking for Python engineer",
            )

            assert result["cv_vector"] is not None
            assert result["jd_vector"] is not None
        finally:
            encoder.vector_store.close()
            os.unlink(db_path)
