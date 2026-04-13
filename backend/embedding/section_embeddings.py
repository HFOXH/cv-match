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

        skills_text = ""
        experience_text = ""
        education_text = ""

        skills = normalized_cv.get("skills")
        if isinstance(skills, list) and skills:
            skills_text = ", ".join(s for s in skills if isinstance(s, str) and s.strip())
            if skills_text:
                section_names.append("skills")
                section_texts.append(skills_text)

        if isinstance(normalized_cv.get("experience_text"), str) and normalized_cv["experience_text"].strip():
            experience_text = normalized_cv["experience_text"].strip()
            section_names.append("experience")
            section_texts.append(experience_text)

        if isinstance(normalized_cv.get("education_text"), str) and normalized_cv["education_text"].strip():
            education_text = normalized_cv["education_text"].strip()
            section_names.append("education")
            section_texts.append(education_text)

        # Always produce an "overall" embedding. Prefer the normalizer's
        # full_text_for_embedding; if missing, stitch sections together so we
        # still get a usable overall vector.
        overall_text = ""
        full_text = normalized_cv.get("full_text_for_embedding")
        if isinstance(full_text, str) and full_text.strip():
            overall_text = full_text.strip()
        else:
            combined = " ".join(t for t in [skills_text, experience_text, education_text] if t).strip()
            if combined:
                overall_text = combined
                logger.info("full_text_for_embedding missing — using combined section text for overall")

        if overall_text:
            section_names.append("overall")
            section_texts.append(overall_text)

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

        all_jd_skills = [
            s for s in (
                (preprocessed_jd.get("required_skills") or [])
                + (preprocessed_jd.get("preferred_skills") or [])
            )
            if isinstance(s, str) and s.strip()
        ]
        if all_jd_skills:
            section_names.append("skills")
            section_texts.append(", ".join(all_jd_skills))

        if isinstance(preprocessed_jd.get("experience_requirements"), str) and preprocessed_jd["experience_requirements"].strip():
            section_names.append("experience")
            section_texts.append(preprocessed_jd["experience_requirements"].strip())

        if isinstance(preprocessed_jd.get("education_requirements"), str) and preprocessed_jd["education_requirements"].strip():
            section_names.append("education")
            section_texts.append(preprocessed_jd["education_requirements"].strip())

        # Always produce an "overall" embedding — prefer cleaned_text, fall back
        # to original_text, else stitch the section texts together.
        overall_text = ""
        for candidate_key in ("cleaned_text", "original_text", "summary"):
            val = preprocessed_jd.get(candidate_key)
            if isinstance(val, str) and val.strip():
                overall_text = val.strip()
                break
        if not overall_text:
            combined = " ".join(t for t in section_texts if t).strip()
            if combined:
                overall_text = combined
                logger.info("JD text fields missing — using combined section text for overall")

        if overall_text:
            section_names.append("overall")
            section_texts.append(overall_text)

        if not section_texts:
            logger.warning("No JD section texts available for embedding")
            return {"skills": None, "experience": None, "education": None, "overall": None}

        embeddings = self.encoder.encode_batch(section_texts)

        result = {"skills": None, "experience": None, "education": None, "overall": None}
        for name, embedding in zip(section_names, embeddings):
            result[name] = embedding

        return result
