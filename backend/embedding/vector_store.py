import json
import logging
import sqlite3
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)

K_DEFAULT_DB_PATH = "vectors.db"


class VectorStore:
    """SQLite-based storage for pre-computed CV embeddings.

    Stores section embeddings as BLOBs and skills list as JSON.
    Prevents re-embedding the same CV on repeated match requests.
    """

    def __init__(self, db_path: str = K_DEFAULT_DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Create the cv_vectors table if it does not exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cv_vectors (
                cv_id TEXT PRIMARY KEY,
                overall_embedding BLOB,
                skills_embedding BLOB,
                experience_embedding BLOB,
                education_embedding BLOB,
                skills_list TEXT,
                raw_text_hash TEXT,
                is_fallback INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_cv_vectors(
        self,
        cv_id: str,
        section_embeddings: Dict[str, Optional[List[float]]],
        skills_list: List[str],
        raw_text_hash: str = "",
        is_fallback: bool = False,
    ):
        """Save all CV vectors and skill list."""
        self.conn.execute(
            """
            INSERT OR REPLACE INTO cv_vectors
            (cv_id, overall_embedding, skills_embedding, experience_embedding,
             education_embedding, skills_list, raw_text_hash, is_fallback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cv_id,
                self._to_blob(section_embeddings.get("overall")),
                self._to_blob(section_embeddings.get("skills")),
                self._to_blob(section_embeddings.get("experience")),
                self._to_blob(section_embeddings.get("education")),
                json.dumps(skills_list),
                raw_text_hash,
                1 if is_fallback else 0,
            ),
        )
        self.conn.commit()
        logger.info("Saved vectors for cv_id=%s (fallback=%s)", cv_id, is_fallback)

    def get_cv_vectors(self, cv_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve CV vectors by cv_id. Returns None if not found."""
        row = self.conn.execute(
            "SELECT overall_embedding, skills_embedding, experience_embedding, "
            "education_embedding, skills_list, is_fallback FROM cv_vectors WHERE cv_id = ?",
            (cv_id,),
        ).fetchone()

        if not row:
            return None

        return {
            "section_embeddings": {
                "overall": self._from_blob(row[0]),
                "skills": self._from_blob(row[1]),
                "experience": self._from_blob(row[2]),
                "education": self._from_blob(row[3]),
            },
            "skills_list": json.loads(row[4]) if row[4] else [],
            "is_fallback": bool(row[5]),
        }

    def delete_cv_vectors(self, cv_id: str):
        """Remove vectors for a CV."""
        self.conn.execute("DELETE FROM cv_vectors WHERE cv_id = ?", (cv_id,))
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()

    @staticmethod
    def _to_blob(embedding: Optional[List[float]]) -> Optional[bytes]:
        if embedding is None:
            return None
        return np.array(embedding, dtype=np.float32).tobytes()

    @staticmethod
    def _from_blob(blob: Optional[bytes]) -> Optional[List[float]]:
        if blob is None:
            return None
        return np.frombuffer(blob, dtype=np.float32).tolist()
