# ocr_utils.py
import fitz  # PyMuPDF
import os
from pathlib import Path
import logging
from PIL import Image
import io
import sys

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ocr_utils")

# Global flag for Tesseract availability
TESSERACT_AVAILABLE = False

def init_tesseract():
    """Initialize Tesseract OCR if available."""
    global TESSERACT_AVAILABLE
    try:
        import pytesseract
        
        # Check for portable Tesseract
        portable_path = Path(__file__).parent / "tesseract" / "tesseract.exe"
        if portable_path.exists():
            pytesseract.pytesseract.tesseract_cmd = str(portable_path)
            logger.info(f"Portable Tesseract found at: {portable_path}")
            TESSERACT_AVAILABLE = True
            return True
        
        # Check common installation paths
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract found at: {path}")
                TESSERACT_AVAILABLE = True
                return True
        
        # Try to find in PATH
        try:
            output = os.popen("tesseract --version").read()
            if "tesseract" in output.lower():
                logger.info("Tesseract found in system PATH")
                TESSERACT_AVAILABLE = True
                return True
        except Exception:
            pass
            
        logger.warning("Tesseract OCR not found. Image-based OCR will be disabled.")
        return False
    except ImportError:
        logger.warning("pytesseract not installed. Image-based OCR disabled.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during Tesseract initialization: {e}")
        return False

# Try to initialize Tesseract
init_tesseract()

def _is_ocr_needed(pdf_path):
    """Pre-checks a PDF to see if it's image-based and likely requires OCR."""
    try:
        with fitz.open(pdf_path) as doc:
            if not doc.is_pdf or doc.is_encrypted:
                return False
            
            text_length = sum(len(page.get_text("text")) for page in doc)
            if text_length < 150:
                return True
    except Exception as e:
        logger.warning(f"Could not pre-check PDF {Path(pdf_path).name} for OCR needs: {e}")
        return True
    return False

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file, using OCR if needed."""
    try:
        pdf_path = Path(pdf_path)
        text = ""
        with fitz.open(pdf_path) as doc:
            text = "".join(page.get_text() for page in doc)
            
        if text and len(text.strip()) > 50:
            logger.info(f"Extracted text directly from {pdf_path.name}")
            return text
            
        if TESSERACT_AVAILABLE:
            logger.info(f"Attempting OCR on {pdf_path.name}")
            return extract_text_with_ocr(pdf_path)
        else:
            logger.warning(f"No text found in {pdf_path.name} and OCR is not available.")
            return ""
    except Exception as exc:
        logger.error(f"Failed to extract text from {pdf_path.name}: {exc}")
        return ""

def extract_text_with_ocr(pdf_path):
    """Extract text from a PDF using basic OCR."""
    if not TESSERACT_AVAILABLE:
        logger.warning("Tesseract OCR not available, cannot perform OCR.")
        return ""
        
    try:
        import pytesseract
        all_text = []
        
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                # Render page at a higher DPI for better quality
                pix = page.get_pixmap(dpi=300)
                img_data = pix.samples
                
                # Convert to PIL Image
                img = Image.open(io.BytesIO(img_data))
                
                # Use Tesseract to do OCR on the image
                page_text = pytesseract.image_to_string(img, lang='eng')
                all_text.append(page_text)
                logger.info(f"OCR processed page {page_num+1} of {pdf_path.name}")
                
        result = "\n\n".join(all_text)
        logger.info(f"OCR extraction complete for {pdf_path.name}: {len(result)} chars")
        return result
    except Exception as e:
        logger.error(f"OCR extraction failed for {pdf_path.name}: {e}")
        return ""