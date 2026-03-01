class ProcessingError(Exception):
    """Raised when CV processing fails (bad file, empty text, etc.)."""
    pass

class ParsingError(Exception):
    """Raised when OpenAI parsing fails (API error, invalid JSON, etc.)."""
    pass
