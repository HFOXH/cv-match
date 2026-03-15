from .cv_service import CVService
from .job_description_service import JDService
from .normalization_service import NormalizationService
from .matching_service import MatchingService

# Shared singleton instances (avoids loading spaCy model multiple times)
job_description_service = JDService()
normalization_service = NormalizationService()
matching_service = MatchingService()
