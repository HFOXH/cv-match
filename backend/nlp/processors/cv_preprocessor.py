import re

class CVPreprocessor:

    @staticmethod
    def preprocess(text: str) -> str:
        if not text:
            return ""

        text = text.replace('\r\n', '\n')

        text = re.sub(r'\s+', ' ', text)

        text = re.sub(r'Work Experience|Professional Experience', 'Experience', text, flags=re.IGNORECASE)
        text = re.sub(r'Education Background|Academic History', 'Education', text, flags=re.IGNORECASE)

        text = text.strip()

        return text