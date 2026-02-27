# /*
# FILE : exceptions.py
# PROJECT : CVMatch - CV Processing Module (Task 1)
# PROGRAMMER : Santiago Cardenas and Amel Sunil
# FIRST VERSION : 2025-02-27
# DESCRIPTION : Custom exception classes for the CV processing pipeline.
#               ProcessingError for file/text issues, ParsingError for
#               OpenAI API failures.
# */


class ProcessingError(Exception):
    """Raised when CV processing fails (bad file, empty text, etc.)."""
    pass


class ParsingError(Exception):
    """Raised when OpenAI parsing fails (API error, invalid JSON, etc.)."""
    pass
