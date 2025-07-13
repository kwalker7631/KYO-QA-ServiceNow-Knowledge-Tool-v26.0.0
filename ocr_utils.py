# ocr_utils.py
# Version: 33.0.0
# Last modified: 2025-07-06

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - optional dependency
    fitz = None
import os
import shutil
from pathlib import Path
import logging
try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional dependency
    Image = None
try:
    import pytesseract
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr_utils")

# --- Tesseract Initialization ---
TESSERACT_AVAILABLE = False
try:
    # Attempt to find Tesseract executable
    tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if not os.path.exists(tesseract_cmd):
        tesseract_cmd = shutil.which("tesseract") # Check PATH

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        TESSERACT_AVAILABLE = True
        logger.info(f"Tesseract found at: {tesseract_cmd}")
    else:
        logger.warning("Tesseract not found. OCR will not be available.")
except Exception as e:
    logger.error(f"Error initializing Tesseract: {e}")


def _is_ocr_needed(pdf_path: str) -> bool:
    """
    Checks if a PDF likely requires OCR by checking for text content.
    Returns True if the document has very little or no extractable text.
    """
    try:
        with fitz.open(pdf_path) as doc:
            text_char_count = 0
            for page in doc:
                text_char_count += len(page.get_text())
                if text_char_count > 100:  # Heuristic threshold
                    return False
        return True
    except Exception as e:
        logger.error(f"Could not pre-check PDF for OCR needs '{pdf_path}': {e}")
        return True # Assume OCR is needed if pre-check fails

def extract_text_from_pdf(pdf_path: str, use_ocr: bool = False) -> str:
    """
    Extracts text from a PDF file. If use_ocr is True and Tesseract is
    available, it will perform OCR on the pages. Otherwise, it extracts
    embedded text.
    """
    all_text = []
    try:
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                if use_ocr and TESSERACT_AVAILABLE:
                    # Perform OCR on the page image
                    pix = page.get_pixmap(dpi=300)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_text = pytesseract.image_to_string(img, lang='eng')
                    all_text.append(page_text)
                else:
                    # Extract embedded text
                    page_text = page.get_text()
                    all_text.append(page_text)
        return "\n".join(all_text)
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e}", exc_info=True)
        return "" # Return empty string on failure
