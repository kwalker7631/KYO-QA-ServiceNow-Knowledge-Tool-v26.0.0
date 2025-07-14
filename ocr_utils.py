# ocr_utils.py
# Version: 2.1.0
# Last modified: 2025-07-13

import logging
from pathlib import Path
from typing import Tuple

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from config import TESSERACT_CMD

logger = logging.getLogger(__name__)

# If Tesseract is not in the system's PATH, set the command path here
# Example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if TESSERACT_CMD and Path(TESSERACT_CMD).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text_from_pdf(pdf_path: str, use_ocr: bool = False) -> Tuple[str, bool]:
    """
    Extracts text from a PDF. If the initial text is empty, it uses OCR as a fallback.

    Args:
        pdf_path: The full path to the PDF file.
        use_ocr: A boolean flag to enable or disable OCR fallback.

    Returns:
        A tuple containing:
        - The extracted text as a string.
        - A boolean indicating if OCR was used (True if an attempt was made, False otherwise).
    """
    extracted_text = ""
    ocr_was_attempted = False

    # --- Step 1: Try standard text extraction ---
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                extracted_text += page.get_text()
        logger.debug(f"Successfully extracted text from {Path(pdf_path).name} using PyMuPDF.")
    except Exception as e:
        logger.error(f"PyMuPDF failed on {pdf_path}: {e}")
        extracted_text = ""  # Ensure text is empty on failure

    # --- Step 2: Fallback to OCR if necessary ---
    if use_ocr and not extracted_text.strip():
        logger.warning(f"No text found in '{Path(pdf_path).name}'. Attempting OCR.")
        ocr_was_attempted = True
        try:
            full_ocr_text = ""
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc):
                    pix = page.get_pixmap(dpi=300)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_text = pytesseract.image_to_string(img)
                    full_ocr_text += page_text
            extracted_text = full_ocr_text
            logger.info(f"OCR successful for '{Path(pdf_path).name}'.")
        except Exception as e:
            logger.error(f"Tesseract OCR failed for {pdf_path}: {e}")
            # If OCR fails, return empty text but indicate an attempt was made
            return "", True

    # --- Final Return ---
    # This is the single point of exit for the function, ensuring two values are always returned.
    return extracted_text, ocr_was_attempted
