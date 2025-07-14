# ocr_utils.py - Fixed version with robust error handling
import fitz  # PyMuPDF
import os
from pathlib import Path
from logging_utils import setup_logger, log_info, log_error, log_warning

logger = setup_logger("ocr_utils")

# Try to import OCR dependencies with fallbacks
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    OCR_DEPENDENCIES_AVAILABLE = True
    log_info(logger, "OCR dependencies loaded successfully")
except ImportError as e:
    OCR_DEPENDENCIES_AVAILABLE = False
    log_warning(logger, f"OCR dependencies not available: {e}")
    log_warning(logger, "Image-based OCR will be disabled")

def init_tesseract():
    """Initialize Tesseract OCR with robust error handling."""
    if not OCR_DEPENDENCIES_AVAILABLE:
        log_warning(logger, "OCR dependencies not available. Skipping Tesseract initialization.")
        return False
        
    try:
        # Strategy 1: Check for portable Tesseract first
        portable_path = Path(__file__).parent / "tesseract" / "tesseract.exe"
        if portable_path.exists():
            try:
                pytesseract.pytesseract.tesseract_cmd = str(portable_path)
                # Test if it works
                version = pytesseract.get_tesseract_version()
                log_info(logger, f"Portable Tesseract found and working: {portable_path} (v{version})")
                return True
            except Exception as e:
                log_warning(logger, f"Portable Tesseract found but not working: {e}")
        
        # Strategy 2: Check common Windows installation paths
        windows_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            Path.home() / "AppData" / "Local" / "Tesseract-OCR" / "tesseract.exe",
        ]
        
        for path in windows_paths:
            if Path(path).exists():
                try:
                    pytesseract.pytesseract.tesseract_cmd = str(path)
                    version = pytesseract.get_tesseract_version()
                    log_info(logger, f"System Tesseract found: {path} (v{version})")
                    return True
                except Exception as e:
                    log_warning(logger, f"Tesseract at {path} not working: {e}")
        
        # Strategy 3: Check if it's in system PATH
        try:
            # Don't set tesseract_cmd, let it use PATH
            version = pytesseract.get_tesseract_version()
            log_info(logger, f"Tesseract found in system PATH (v{version})")
            return True
        except Exception as e:
            log_warning(logger, f"Tesseract not found in PATH: {e}")
        
        # Strategy 4: Try to find it with 'where' command on Windows
        if os.name == 'nt':
            try:
                result = os.popen("where tesseract").read().strip()
                if result and Path(result).exists():
                    pytesseract.pytesseract.tesseract_cmd = result
                    version = pytesseract.get_tesseract_version()
                    log_info(logger, f"Tesseract found with 'where' command: {result} (v{version})")
                    return True
            except Exception:
                pass
        
        # All strategies failed
        log_warning(logger, "Tesseract OCR not found. Image-based OCR will be disabled.")
        log_info(logger, "To enable OCR, install Tesseract from: https://github.com/tesseract-ocr/tesseract")
        return False
        
    except Exception as e:
        log_error(logger, f"Unexpected error during Tesseract initialization: {e}")
        return False

# Initialize Tesseract
TESSERACT_AVAILABLE = init_tesseract()

def _is_ocr_needed(pdf_path):
    """
    Pre-checks a PDF to see if it's image-based and likely requires OCR.
    Returns True if OCR is needed, False if direct text extraction should work.
    """
    try:
        pdf_path = Path(pdf_path)
        
        with fitz.open(pdf_path) as doc:
            if not doc.is_pdf:
                log_warning(logger, f"{pdf_path.name} is not a valid PDF")
                return False
                
            if doc.is_encrypted:
                log_warning(logger, f"{pdf_path.name} is encrypted/password protected")
                return False
            
            # Check first few pages for text content
            pages_to_check = min(3, len(doc))  # Check up to 3 pages
            total_text_length = 0
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
                text = page.get_text("text")
                total_text_length += len(text.strip())
            
            # If we found very little text across multiple pages, probably needs OCR
            avg_text_per_page = total_text_length / pages_to_check
            threshold = 100  # characters per page
            
            needs_ocr = avg_text_per_page < threshold
            
            if needs_ocr:
                log_info(logger, f"{pdf_path.name} appears to be image-based (avg {avg_text_per_page:.0f} chars/page)")
            else:
                log_info(logger, f"{pdf_path.name} appears to have embedded text (avg {avg_text_per_page:.0f} chars/page)")
            
            return needs_ocr
            
    except Exception as e:
        log_warning(logger, f"Could not pre-check PDF {Path(pdf_path).name} for OCR needs: {e}")
        # If we can't determine, assume it might need OCR
        return True

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file with hybrid approach:
    1. Try direct text extraction first
    2. Fall back to OCR if needed and available
    """
    try:
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            log_error(logger, f"PDF file not found: {pdf_path}")
            return ""
        
        log_info(logger, f"Starting text extraction from {pdf_path.name}")
        
        # First attempt: Direct text extraction
        text = ""
        with fitz.open(pdf_path) as doc:
            if doc.is_encrypted:
                log_error(logger, f"PDF is encrypted: {pdf_path.name}")
                return ""
                
            for page in doc:
                page_text = page.get_text("text")
                text += page_text + "\n"
        
        # Check if we got sufficient text
        text_length = len(text.strip())
        
        if text_length > 200:  # Arbitrary threshold for "sufficient" text
            log_info(logger, f"Direct extraction successful: {text_length} characters from {pdf_path.name}")
            return text
        
        log_info(logger, f"Direct extraction yielded only {text_length} characters, trying OCR...")
        
        # Second attempt: OCR if available
        if TESSERACT_AVAILABLE and OCR_DEPENDENCIES_AVAILABLE:
            ocr_text = extract_text_with_ocr(pdf_path)
            if ocr_text and len(ocr_text.strip()) > text_length:
                log_info(logger, f"OCR extraction successful: {len(ocr_text)} characters from {pdf_path.name}")
                return ocr_text
            else:
                log_warning(logger, f"OCR did not improve text extraction for {pdf_path.name}")
                return text  # Return what we got from direct extraction
        else:
            log_warning(logger, f"OCR not available for {pdf_path.name}, using direct extraction result")
            return text
            
    except Exception as exc:
        log_error(logger, f"Failed to extract text from {pdf_path}: {exc}")
        return ""

def extract_text_with_ocr(pdf_path):
    """
    Extract text from a PDF using OCR with enhanced preprocessing.
    Returns empty string if OCR is not available or fails.
    """
    if not TESSERACT_AVAILABLE or not OCR_DEPENDENCIES_AVAILABLE:
        log_warning(logger, "OCR not available for text extraction")
        return ""
        
    all_text = []
    
    try:
        pdf_path = Path(pdf_path)
        log_info(logger, f"Starting OCR extraction for {pdf_path.name}")
        
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                try:
                    # Render page at higher DPI for better OCR accuracy
                    dpi = 300  # Good balance between quality and processing time
                    pix = page.get_pixmap(dpi=dpi)
                    
                    # Convert to numpy array
                    img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                    
                    # Handle different color formats
                    if pix.n == 4:  # RGBA
                        img_cv = cv2.cvtColor(img_data, cv2.COLOR_RGBA2BGR)
                    elif pix.n == 3:  # RGB
                        img_cv = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
                    else:  # Grayscale
                        img_cv = img_data

                    # Preprocessing for better OCR
                    # Convert to grayscale if not already
                    if len(img_cv.shape) == 3:
                        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = img_cv

                    # Apply adaptive thresholding for better text contrast
                    binary_img = cv2.adaptiveThreshold(
                        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                    )

                    # Optional: Noise reduction (can help with poor quality scans)
                    denoised = cv2.medianBlur(binary_img, 3)

                    # OCR configuration for better accuracy
                    # --psm 6: Assume a single uniform block of text
                    # --oem 3: Use both legacy and LSTM OCR engines
                    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,;:!?()-_/'
                    
                    # Perform OCR
                    page_text = pytesseract.image_to_string(
                        denoised, 
                        lang='eng',  # Add other languages if needed: 'eng+jpn'
                        config=custom_config
                    )
                    
                    all_text.append(page_text)
                    log_info(logger, f"OCR completed page {page_num+1}/{len(doc)} of {pdf_path.name}")
                    
                except Exception as e:
                    log_warning(logger, f"OCR failed for page {page_num+1} of {pdf_path.name}: {e}")
                    all_text.append("")  # Add empty text for failed page
                
        result = "\n\n".join(all_text)
        log_info(logger, f"OCR extraction complete for {pdf_path.name}: {len(result)} characters")
        return result
        
    except Exception as e:
        log_error(logger, f"OCR extraction failed for {pdf_path}: {e}")
        return ""

def test_ocr_functionality():
    """Test OCR functionality for diagnostics"""
    results = {
        "ocr_dependencies": OCR_DEPENDENCIES_AVAILABLE,
        "tesseract_available": TESSERACT_AVAILABLE,
        "tesseract_version": None,
        "tesseract_path": None
    }
    
    if TESSERACT_AVAILABLE and OCR_DEPENDENCIES_AVAILABLE:
        try:
            results["tesseract_version"] = pytesseract.get_tesseract_version()
            results["tesseract_path"] = pytesseract.pytesseract.tesseract_cmd
        except Exception as e:
            log_warning(logger, f"Could not get Tesseract details: {e}")
    
    return results

# Test functionality on import for debugging
if __name__ == "__main__":
    print("OCR Utils - Diagnostic Information")
    print("=" * 40)
    
    test_results = test_ocr_functionality()
    
    print(f"OCR Dependencies Available: {test_results['ocr_dependencies']}")
    print(f"Tesseract Available: {test_results['tesseract_available']}")
    
    if test_results['tesseract_version']:
        print(f"Tesseract Version: {test_results['tesseract_version']}")
        print(f"Tesseract Path: {test_results['tesseract_path']}")
    
    if not test_results['tesseract_available']:
        print("\nTo enable OCR functionality:")
        print("1. Install Tesseract-OCR from: https://github.com/tesseract-ocr/tesseract")
        print("2. Ensure it's added to your system PATH")
        print("3. Or place portable Tesseract in 'tesseract/' folder")
