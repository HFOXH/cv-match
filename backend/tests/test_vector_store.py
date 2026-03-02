import os
import tempfile

from embedding.vector_store import VectorStore


def _make_store():
    """Create a VectorStore with a temporary database."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    return VectorStore(db_path=tmp.name), tmp.name


def _sample_embeddings():
    return {
        "overall": [0.1, 0.2, 0.3],
        "skills": [0.4, 0.5, 0.6],
        "experience": [0.7, 0.8, 0.9],
        "education": [1.0, 1.1, 1.2],
    }


class TestVectorStore:
    """Tests for SQLite vector storage."""

    def test_save_and_retrieve_roundtrip(self):
        store, db_path = _make_store()
        try:
            embeddings = _sample_embeddings()
            store.save_cv_vectors(
                cv_id="test-123",
                section_embeddings=embeddings,
                skills_list=["python", "react"],
            )

            result = store.get_cv_vectors("test-123")

            assert result is not None
            assert result["skills_list"] == ["python", "react"]
            assert result["is_fallback"] is False
            for key in ["overall", "skills", "experience", "education"]:
                for a, b in zip(result["section_embeddings"][key], embeddings[key]):
                    assert abs(a - b) < 0.001
        finally:
            store.close()
            os.unlink(db_path)

    def test_get_nonexistent_returns_none(self):
        store, db_path = _make_store()
        try:
            result = store.get_cv_vectors("does-not-exist")
            assert result is None
        finally:
            store.close()
            os.unlink(db_path)

    def test_overwrite_existing(self):
        store, db_path = _make_store()
        try:
            store.save_cv_vectors(
                cv_id="test-123",
                section_embeddings=_sample_embeddings(),
                skills_list=["python"],
            )
            store.save_cv_vectors(
                cv_id="test-123",
                section_embeddings={"overall": [9.0, 9.0], "skills": None,
                                    "experience": None, "education": None},
                skills_list=["java"],
            )

            result = store.get_cv_vectors("test-123")
            assert result["skills_list"] == ["java"]
            assert abs(result["section_embeddings"]["overall"][0] - 9.0) < 0.001
        finally:
            store.close()
            os.unlink(db_path)

    def test_null_sections(self):
        store, db_path = _make_store()
        try:
            store.save_cv_vectors(
                cv_id="test-123",
                section_embeddings={
                    "overall": [0.1, 0.2],
                    "skills": None,
                    "experience": None,
                    "education": None,
                },
                skills_list=[],
                is_fallback=True,
            )

            result = store.get_cv_vectors("test-123")
            assert result["section_embeddings"]["overall"] is not None
            assert result["section_embeddings"]["skills"] is None
            assert result["section_embeddings"]["experience"] is None
            assert result["section_embeddings"]["education"] is None
            assert result["is_fallback"] is True
        finally:
            store.close()
            os.unlink(db_path)

    def test_delete(self):
        store, db_path = _make_store()
        try:
            store.save_cv_vectors(
                cv_id="test-123",
                section_embeddings=_sample_embeddings(),
                skills_list=["python"],
            )
            store.delete_cv_vectors("test-123")

            result = store.get_cv_vectors("test-123")
            assert result is None
        finally:
            store.close()
            os.unlink(db_path)
