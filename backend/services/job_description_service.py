from nlp_preprocessing.job_preprocessor import JobDescriptionPreprocessor

class JDService:

    def __init__(self):
        self.processor = JobDescriptionPreprocessor()

    def process(self, text: str):
        return self.processor.preprocess(text)