from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class MatchingService:

    @staticmethod
    def compute_match(cv_embedding, jd_embedding):
        similarity = cosine_similarity(
            [cv_embedding],
            [jd_embedding]
        )[0][0]

        percentage = round(similarity * 100, 2)

        return percentage