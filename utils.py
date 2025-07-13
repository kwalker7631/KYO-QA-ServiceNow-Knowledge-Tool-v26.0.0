"""Consolidated helper utilities.

Sections:
1. AI Extraction
2. Excel Generation
3. Custom Exceptions
4. Custom Patterns
5. Translation Helpers
6. Error Tracking
7. Recycle Helpers
"""

# --- 1. AI Extraction ---
from data_harvesters import (
    harvest_all_data as ai_extract,
    harvest_author as harvest_metadata,
)

import importlib
import logging
import os
import re
import types
from contextlib import nullcontext
from functools import lru_cache

try:
    from extract.common import bulletproof_extraction
except Exception:  # fallback using regex

    def bulletproof_extraction(text, patterns=None):
        results = []
        if patterns:
            for pattern in patterns:
                try:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    results.extend(matches)
                except re.error:
                    continue
        return results


__all__ = [
    "ai_extract",
    "harvest_metadata",
    "bulletproof_extraction",
]

# --- 2. Excel Generation ---

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional
    pd = types.SimpleNamespace(
        DataFrame=lambda *a, **k: [], ExcelWriter=lambda *a, **k: nullcontext()
    )
logger = logging.getLogger(__name__)


class ExcelGenerator:
    def __init__(self, output_filepath):
        self.output_filepath = output_filepath

    def create_report(self, data):
        df = pd.DataFrame(data or [])
        try:
            with pd.ExcelWriter(self.output_filepath, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="QA_Report", index=False)
        except Exception as e:  # pragma: no cover - best effort
            logger.error(f"Failed to create Excel report: {e}")
            raise


# --- 3. Custom Exceptions ---
class KYOQAToolError(Exception):
    """Base exception for all KYO QA Tool errors."""


class FileLockError(KYOQAToolError):
    """Raised when a file is locked by another process."""


class ExcelGenerationError(KYOQAToolError):
    """Raised when Excel file generation fails."""


class PDFExtractionError(KYOQAToolError):
    """Raised when PDF text extraction fails."""


class PatternMatchError(KYOQAToolError):
    """Raised when pattern matching fails."""


class ConfigurationError(KYOQAToolError):
    """Raised when there's a configuration issue."""


# --- 4. Custom Patterns ---
MODEL_PATTERNS = [
    r"\b(TASKalfa|ECOSYS)\s*[\w-]+\b",
    r"\b(PF|DF|MK|AK|DP|BF|JS)-\d+[\w-]*\b",
    r"\bFS-C?\d+[a-zA-Z]*\b",
    r"\bKM-\d+[a-zA-Z]*\b",
    r"\bCS\s\d+[a-zA-Z]*\b",
    r"\bTASKalfa\s+\d+(ci|cxi|cx)\b",
    r"\bECOSYS\s+M\d+(cdn|cdnl|ci|cidn)\b",
    r"\bECOSYS\s+P\d+(dn|dtn|d)\b",
    r"\bDP-\d+\b",
    r"\bM\d+idn\b",
    r"\bM\d+idnf\b",
    r"\bVi\d+\b",
    r"\b[A-Z]{2,}-\d{3,}\b",
    r"\b[A-Z]{3,}\s[A-Z]\d{4}[a-z]*\b",
    r"\bP\d+cdn\b",
    r"\bP\d+d\b",
    r"\bP\d+dn\b",
    r"\bM\d+dn\b",
]

QA_NUMBER_PATTERNS = [
    r"\bQA[-_]?\d+[\w-]*\b",
    r"\bSB[-_]?\d+[\w-]*\b",
]

PART_NUMBER_PATTERNS = [
    r"\b\d{2,}[A-Z]{1,}\d{5,}\b",
]

# --- 5. Translation Helpers ---


@lru_cache(maxsize=1)
def _get_translator():
    try:
        gt = importlib.import_module("googletrans")
        return gt.Translator()
    except Exception:
        return None


def auto_translate_text(text: str, target_lang: str = "en") -> str | None:
    translator = _get_translator()
    if translator is None:
        return text
    try:
        detected = translator.detect(text).lang
        if detected == target_lang or detected not in {"ja", "es", "de"}:
            return text
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception:
        return None


# --- 6. Error Tracking ---

try:
    from sentry_sdk import init
    from sentry_sdk.integrations.logging import LoggingIntegration, EventHandler
except Exception:  # pragma: no cover - optional
    init = None
    LoggingIntegration = None
    EventHandler = None

_initialized = False
_handler: logging.Handler | None = None


def init_error_tracker() -> bool:
    global _initialized, _handler
    if _initialized:
        return True
    dsn = os.getenv("SENTRY_DSN")
    if not dsn or not init:
        return False
    sentry_logging = LoggingIntegration(level=logging.ERROR, event_level=logging.ERROR)
    init(dsn=dsn, integrations=[sentry_logging])
    _handler = EventHandler(level=logging.ERROR)
    _initialized = True
    return True


def get_handler() -> logging.Handler | None:
    return _handler


# --- 7. Recycle Helpers ---

DEFAULT_RECYCLING_RULES = [
    (r"\s{2,}", " "),
]
try:
    from custom_recycles import RECYCLING_RULES as CUSTOM_RECYCLING_RULES
except Exception:
    CUSTOM_RECYCLING_RULES = []

RECYCLING_RULES = CUSTOM_RECYCLING_RULES + [
    r for r in DEFAULT_RECYCLING_RULES if r not in CUSTOM_RECYCLING_RULES
]


def apply_recycles(text: str, rules=None) -> str:
    if not text:
        return ""
    if rules is None:
        rules = RECYCLING_RULES
    for pattern, repl in rules:
        try:
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
        except re.error:
            continue
    return text
