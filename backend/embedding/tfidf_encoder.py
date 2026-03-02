import logging
from typing import Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import spmatrix

logger = logging.getLogger(__name__)

K_MAX_FEATURES = 5000
K_NGRAM_RANGE = (1, 3)
K_MIN_DF = 1
K_MAX_DF = 0.8


class TFIDFEncoder:
    """TF-IDF vectorization for keyword-level similarity between CV and JD text."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=K_MAX_FEATURES,
            ngram_range=K_NGRAM_RANGE,
            min_df=K_MIN_DF,
            max_df=K_MAX_DF,
            stop_words="english",
        )
        self._is_fitted = False

    def fit_and_transform(self, cv_text: str, jd_text: str) -> Dict[str, spmatrix]:
        """Fit on both texts and return sparse TF-IDF vectors.

        Parameters:
            cv_text: Full CV text (raw or cleaned).
            jd_text: Cleaned job description text.

        Returns:
            Dict with "cv_vector" and "jd_vector" as sparse matrices.
        """
        if not cv_text.strip() or not jd_text.strip():
            logger.warning("Empty text provided to TF-IDF encoder")
            return {"cv_vector": None, "jd_vector": None}

        vectors = self.vectorizer.fit_transform([cv_text, jd_text])
        self._is_fitted = True
        return {
            "cv_vector": vectors[0],
            "jd_vector": vectors[1],
        }
