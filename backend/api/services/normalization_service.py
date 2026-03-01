from nlp_preprocessing.cv_normalizer import CVDataNormalizer

class NormalizationService:

    def __init__(self):
        self.normalizer = CVDataNormalizer()

    def normalize(self, parsed_data: dict):
        return self.normalizer.normalize(parsed_data)