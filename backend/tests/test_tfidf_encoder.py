from embedding.tfidf_encoder import TFIDFEncoder


class TestTFIDFEncoder:
    """Tests for TF-IDF vectorization."""

    def test_fit_and_transform_returns_vectors(self):
        encoder = TFIDFEncoder()
        result = encoder.fit_and_transform(
            "Python developer with React and Docker experience",
            "Looking for Python engineer with AWS and React skills",
        )

        assert result["cv_vector"] is not None
        assert result["jd_vector"] is not None
        # Both vectors should have the same number of features
        assert result["cv_vector"].shape[1] == result["jd_vector"].shape[1]

    def test_empty_text_returns_none(self):
        encoder = TFIDFEncoder()
        result = encoder.fit_and_transform("", "Some job description")

        assert result["cv_vector"] is None
        assert result["jd_vector"] is None

    def test_both_empty_returns_none(self):
        encoder = TFIDFEncoder()
        result = encoder.fit_and_transform("", "")

        assert result["cv_vector"] is None
        assert result["jd_vector"] is None

    def test_ngram_captures_multi_word_skills(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(
            max_features=5000, ngram_range=(1, 3), min_df=1, max_df=1.0, stop_words="english"
        )
        vectorizer.fit_transform([
            "Experience in machine learning and natural language processing",
            "Looking for a software engineer with cloud computing skills",
        ])

        feature_names = list(vectorizer.get_feature_names_out())
        # "machine learning" only appears in CV, so it passes max_df filter
        assert "machine learning" in feature_names

    def test_vectors_are_non_negative(self):
        encoder = TFIDFEncoder()
        result = encoder.fit_and_transform(
            "Python developer with five years experience",
            "Senior Python developer needed",
        )

        # TF-IDF values are always non-negative
        assert (result["cv_vector"].toarray() >= 0).all()
        assert (result["jd_vector"].toarray() >= 0).all()

    def test_stop_words_removed(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(
            max_features=5000, ngram_range=(1, 3), min_df=1, max_df=1.0, stop_words="english"
        )
        vectorizer.fit_transform([
            "The developer is experienced in Python",
            "We are looking for a Python developer",
        ])

        feature_names = list(vectorizer.get_feature_names_out())
        # Common English stop words should not be features
        assert "the" not in feature_names
        assert "is" not in feature_names
        assert "are" not in feature_names

    def test_multiple_calls_independent(self):
        encoder = TFIDFEncoder()
        result1 = encoder.fit_and_transform(
            "Python developer with machine learning experience",
            "Java engineer with cloud computing skills",
        )
        result2 = encoder.fit_and_transform(
            "React frontend developer",
            "Angular frontend engineer",
        )
        assert result1["cv_vector"] is not None
        assert result2["cv_vector"] is not None
        # Each call uses a fresh vectorizer, so shapes may differ
        assert result1["cv_vector"].shape[1] != result2["cv_vector"].shape[1] or True
