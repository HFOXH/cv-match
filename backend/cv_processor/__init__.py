"""CV Processor package.

Provides the main CVProcessor class for extracting and parsing CV files.

Authors: Santiago Cardenas and Amel Sunil
First version: 2025-02-27
"""

from .processor import CVProcessor
from .exceptions import ProcessingError, ParsingError

__all__ = ["CVProcessor", "ProcessingError", "ParsingError"]
