"""Central configuration for the CVMatch backend.

Every tunable constant — OpenAI model names, scoring weights, sigmoid
calibration parameters, file size limits — lives here so the codebase
can be reconfigured without editing logic files.

Model names are env-overridable. Scoring knobs are kept as Python
constants (they shouldn't change without a retraining / re-evaluation).
"""

import os
from dotenv import load_dotenv

load_dotenv()



# OpenAI model selection  (env-overridable)


CV_PARSER_MODEL      = os.getenv("CV_PARSER_MODEL",      "gpt-4o-mini")
CV_NORMALIZER_MODEL  = os.getenv("CV_NORMALIZER_MODEL",  "gpt-4o-mini")
JD_EXTRACTOR_MODEL   = os.getenv("JD_EXTRACTOR_MODEL",   "gpt-4o-mini")
SEMANTIC_MATCH_MODEL = os.getenv("SEMANTIC_MATCH_MODEL", "gpt-4o-mini")

EMBEDDING_MODEL      = os.getenv("EMBEDDING_MODEL",      "text-embedding-3-small")
EMBEDDING_DIMS       = 1536



# Scoring engine  (not env-overridable — changing these changes scoring behavior)


# Sigmoid calibration: maps raw weighted similarity (0–1) to a human-readable
# 0–100% match. See docs/TECHNICAL_GUIDE.md for the curve.
SIGMOID_STEEPNESS = 8
SIGMOID_MIDPOINT  = 0.30

# Weighted blend of five signals. Must sum to 1.0.
WEIGHTS = {
    "skills_jaccard":   0.25,
    "skills_semantic":  0.10,
    "sbert_overall":    0.30,
    "experience_match": 0.25,
    "education_match":  0.10,
}


# Limits


MAX_FILE_SIZE        = 5 * 1024 * 1024   # 5 MB — maximum uploaded CV size
MAX_CV_TEXT_LENGTH   = 6000              # characters sent to the CV parser
MAX_EMBEDDING_INPUT  = 8000              # characters sent to the embedding API
