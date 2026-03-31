import os
import logging
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv
from services.openai_retry import retry_openai_call

load_dotenv()

logger = logging.getLogger(__name__)

K_EMBEDDING_MODEL = "text-embedding-3-small"
K_EMBEDDING_DIMS = 1536
K_MAX_INPUT_LENGTH = 8000


class OpenAIEncoder:
    """Wrapper around OpenAI's text-embedding-3-small API.

    Produces 1536-dimensional embeddings. Handles initialization
    failure gracefully (logs error, returns None on encode).
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            logger.error("No OpenAI API key provided. Embedding generation will not work.")

        self.model = K_EMBEDDING_MODEL
        self.dims = K_EMBEDDING_DIMS
        logger.info("OpenAIEncoder initialized (model=%s, dims=%d)", self.model, self.dims)

    def encode(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text.

        Returns:
            List of floats (1536 dims) or None if encoding fails.
        """
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate embedding.")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided to OpenAI encoder")
            return None

        try:
            truncated = text[:K_MAX_INPUT_LENGTH]
            response = retry_openai_call(
                self.client.embeddings.create,
                model=self.model,
                input=truncated,
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error("OpenAI embedding API call failed: %s", e)
            return None

    def encode_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts in a single API call.

        Returns:
            List of embeddings (same order as input). None for any that failed.
        """
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate embeddings.")
            return [None] * len(texts)

        valid_texts = []
        indices = []
        for i, t in enumerate(texts):
            if t and t.strip():
                valid_texts.append(t[:K_MAX_INPUT_LENGTH])
                indices.append(i)

        if not valid_texts:
            return [None] * len(texts)

        try:
            response = retry_openai_call(
                self.client.embeddings.create,
                model=self.model,
                input=valid_texts,
            )

            results = [None] * len(texts)
            for j, emb_data in enumerate(response.data):
                results[indices[j]] = emb_data.embedding
            return results

        except Exception as e:
            logger.error("OpenAI batch embedding API call failed: %s", e)
            return [None] * len(texts)
