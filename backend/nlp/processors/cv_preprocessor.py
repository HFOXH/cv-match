import re
class CVPreprocessor:

    @staticmethod
    def preprocess(text: str) -> str:
        if not text:
            return ""

        # Normalizar line endings
        text = text.replace('\r\n', '\n')

        # Eliminar espacios múltiples SOLO dentro de líneas
        lines = []
        for line in text.split('\n'):
            cleaned = re.sub(r'[ \t]+', ' ', line).strip()
            lines.append(cleaned)

        text = "\n".join(lines)

        # Normalizar headings sin romper estructura
        text = re.sub(
            r'Professional Experience|Work Experience',
            'Experience',
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r'Education Background|Academic History',
            'Education',
            text,
            flags=re.IGNORECASE
        )

        return text.strip()