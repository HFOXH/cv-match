import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class SectionEmbeddingGenerator:
    """Generate separate embeddings for CV and JD sections.

    Uses an encoder (OpenAIEncoder) to produce embeddings for each
    section: skills, experience, education, overall.
    """

    def __init__(self, encoder):
        """Initialize with any encoder that has encode() and encode_batch() methods."""
        self.encoder = encoder

    def generate_cv_section_embeddings(
        self, normalized_cv: Dict[str, Any]
    ) -> Dict[str, Optional[List[float]]]:
        """Generate embeddings for each CV section.

        Input: normalized CV data from CVDataNormalizer.normalize() with keys:
            - skills: list of skill strings
            - experience_text: combined experience paragraph
            - education_text: combined education paragraph
            - full_text_for_embedding: complete profile summary

        Returns:
            Dict mapping section names to embedding vectors (or None).
        """
        section_names = []
        section_texts = []

        if normalized_cv.get("skills"):
            section_names.append("skills")
            section_texts.append(", ".join(normalized_cv["skills"]))

        if normalized_cv.get("experience_text"):
            section_names.append("experience")
            section_texts.append(normalized_cv["experience_text"])

        if normalized_cv.get("education_text"):
            section_names.append("education")
            section_texts.append(normalized_cv["education_text"])

        if normalized_cv.get("full_text_for_embedding"):
            section_names.append("overall")
            section_texts.append(normalized_cv["full_text_for_embedding"])

        if not section_texts:
            logger.warning("No CV section texts available for embedding")
            return {"skills": None, "experience": None, "education": None, "overall": None}

        embeddings = self.encoder.encode_batch(section_texts)

        result = {"skills": None, "experience": None, "education": None, "overall": None}
        for name, embedding in zip(section_names, embeddings):
            result[name] = embedding

        return result

    def generate_jd_section_embeddings(
        self, preprocessed_jd: Dict[str, Any]
    ) -> Dict[str, Optional[List[float]]]:
        """Generate embeddings for job description sections.

        Input: preprocessed JD data from JobDescriptionPreprocessor.preprocess() with keys:
            - required_skills: list of required skill strings
            - preferred_skills: list of preferred skill strings
            - cleaned_text: cleaned full JD text

        Returns:
            Dict mapping section names to embedding vectors (or None).
        """
        section_names = []
        section_texts = []

        all_jd_skills = (
            preprocessed_jd.get("required_skills", [])
            + preprocessed_jd.get("preferred_skills", [])
        )
        if all_jd_skills:
            section_names.append("skills")
            section_texts.append(", ".join(all_jd_skills))

        if preprocessed_jd.get("cleaned_text"):
            section_names.append("overall")
            section_texts.append(preprocessed_jd["cleaned_text"])

        if not section_texts:
            logger.warning("No JD section texts available for embedding")
            return {"skills": None, "overall": None}

        embeddings = self.encoder.encode_batch(section_texts)

        result = {"skills": None, "overall": None}
        for name, embedding in zip(section_names, embeddings):
            result[name] = embedding

        return result
