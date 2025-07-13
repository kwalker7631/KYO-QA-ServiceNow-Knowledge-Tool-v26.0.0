# custom_exceptions.py - Custom exception classes for KYO QA Tool

from utils import (
    KYOQAToolError,
    FileLockError,
    ExcelGenerationError,
    PDFExtractionError,
    PatternMatchError,
    ConfigurationError,
)

__all__ = [
    "KYOQAToolError",
    "FileLockError",
    "ExcelGenerationError",
    "PDFExtractionError",
    "PatternMatchError",
    "ConfigurationError",
]
