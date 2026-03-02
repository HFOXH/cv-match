from unittest.mock import patch, MagicMock

from embedding.openai_encoder import OpenAIEncoder


def _mock_embedding(values):
    """Create a mock embedding response."""
    emb = MagicMock()
    emb.embedding = values
    return emb


def _mock_embedding_response(embeddings_list):
    """Create a mock OpenAI embeddings.create response."""
    response = MagicMock()
    response.data = [_mock_embedding(v) for v in embeddings_list]
    return response


class TestEncode:
    """Tests for single text encoding."""

    @patch("embedding.openai_encoder.OpenAI")
    def test_encode_returns_embedding(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.embeddings.create.return_value = _mock_embedding_response(
            [[0.1, 0.2, 0.3]]
        )

        encoder = OpenAIEncoder(openai_api_key="test-key")
        result = encoder.encode("Python developer")

        assert result == [0.1, 0.2, 0.3]
        mock_client.embeddings.create.assert_called_once()

    @patch("embedding.openai_encoder.OpenAI")
    def test_encode_returns_none_on_api_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.embeddings.create.side_effect = Exception("API Error")

        encoder = OpenAIEncoder(openai_api_key="test-key")
        result = encoder.encode("Python developer")

        assert result is None

    @patch("embedding.openai_encoder.OpenAI")
    def test_encode_returns_none_on_empty_text(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        encoder = OpenAIEncoder(openai_api_key="test-key")
        result = encoder.encode("")

        assert result is None
        mock_client.embeddings.create.assert_not_called()

    @patch.dict("os.environ", {}, clear=True)
    def test_encode_returns_none_when_no_client(self):
        encoder = OpenAIEncoder(openai_api_key=None)
        result = encoder.encode("Python developer")

        assert result is None

    @patch("embedding.openai_encoder.OpenAI")
    def test_encode_truncates_long_text(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.embeddings.create.return_value = _mock_embedding_response(
            [[0.1, 0.2]]
        )

        encoder = OpenAIEncoder(openai_api_key="test-key")
        long_text = "a" * 10000
        encoder.encode(long_text)

        # Check that the input was truncated to 8000 chars
        call_args = mock_client.embeddings.create.call_args
        assert len(call_args.kwargs["input"]) == 8000


class TestEncodeBatch:
    """Tests for batch encoding."""

    @patch("embedding.openai_encoder.OpenAI")
    def test_encode_batch_returns_embeddings(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.embeddings.create.return_value = _mock_embedding_response(
            [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        )

        encoder = OpenAIEncoder(openai_api_key="test-key")
        result = encoder.encode_batch(["text1", "text2", "text3"])

        assert len(result) == 3
        assert result[0] == [0.1, 0.2]
        assert result[1] == [0.3, 0.4]
        assert result[2] == [0.5, 0.6]

    @patch("embedding.openai_encoder.OpenAI")
    def test_encode_batch_handles_empty_strings(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.embeddings.create.return_value = _mock_embedding_response(
            [[0.1, 0.2]]
        )

        encoder = OpenAIEncoder(openai_api_key="test-key")
        result = encoder.encode_batch(["valid text", "", "  "])

        assert len(result) == 3
        assert result[0] == [0.1, 0.2]
        assert result[1] is None  # empty string
        assert result[2] is None  # whitespace only

    @patch("embedding.openai_encoder.OpenAI")
    def test_encode_batch_returns_none_on_api_error(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.embeddings.create.side_effect = Exception("API Error")

        encoder = OpenAIEncoder(openai_api_key="test-key")
        result = encoder.encode_batch(["text1", "text2"])

        assert result == [None, None]

    @patch("embedding.openai_encoder.OpenAI")
    def test_encode_batch_all_empty_returns_nones(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        encoder = OpenAIEncoder(openai_api_key="test-key")
        result = encoder.encode_batch(["", ""])

        assert result == [None, None]
        mock_client.embeddings.create.assert_not_called()
