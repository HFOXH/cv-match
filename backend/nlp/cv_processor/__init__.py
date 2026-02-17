"""CV Processor Module for extracting and structuring resume information."""

# Lazy imports to avoid circular dependencies and missing packages
def __getattr__(name):
    if name == "CVProcessor":
        from .cv_processor import CVProcessor
        return CVProcessor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["CVProcessor"]
