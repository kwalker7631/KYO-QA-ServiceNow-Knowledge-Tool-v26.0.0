# processing_engine.py
import shutil
import time
import json
import logging
import queue
import threading
import tempfile
import zipfile
from logging_config import configure_logging
from pathlib import Path
from datetime import datetime
import traceback
from processing_helpers import fetch_data, parse_data, export_results

# Set up logging
logger = configure_logging("processing_engine")

# Try to import required modules, with fallbacks where possible
try:
    import openpyxl
    from openpyxl.styles import PatternFill
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    logger.warning("openpyxl not installed - Excel processing will not work")
    OPENPYXL_AVAILABLE = False

try:
    from config import PDF_TXT_DIR, OUTPUT_DIR, CACHE_DIR, META_COLUMN_NAME, AUTHOR_COLUMN_NAME, STATUS_COLUMN_NAME, DESCRIPTION_COLUMN_NAME
except ImportError:
    # Fallback configuration
    logger.warning("Could not import config, using default values")
    BASE_DIR = Path(__file__).parent
    PDF_TXT_DIR = BASE_DIR / "PDF_TXT"
    OUTPUT_DIR = BASE_DIR / "output"
    CACHE_DIR = BASE_DIR / ".cache"
    META_COLUMN_NAME = "Meta"
    AUTHOR_COLUMN_NAME = "Author"
    STATUS_COLUMN_NAME = "Processing Status"
    DESCRIPTION_COLUMN_NAME = "Short description"

# FIXED: Removed unused FileLockError import

try:
    from data_harvesters import harvest_all_data
except ImportError:
    logger.error("data_harvesters module not found, processing will fail")
    def harvest_all_data(text, filename):
        return {"models": "Not Found", "author": ""}

try:
    from file_utils import is_file_locked
except ImportError:
    def is_file_locked(filepath):
        """Check if a file is locked by attempting to open it in append mode."""
        try:
            with open(filepath, "a+b"):
                pass
            return False
        except (IOError, PermissionError):
            return True

try:
    from ocr_utils import extract_text_from_pdf, _is_ocr_needed
except ImportError:
    logger.error("ocr_utils module not found, text extraction will fail")
    def extract_text_from_pdf(pdf_path):
        return ""
    def _is_ocr_needed(pdf_path):
        return False

# Ensure all necessary directories exist
def ensure_directories():
    """Create all necessary directories for the application."""
    for directory in [PDF_TXT_DIR, OUTPUT_DIR, CACHE_DIR, PDF_TXT_DIR / "needs_review"]:
        directory.mkdir(parents=True, exist_ok=True)

# Call this at module import to ensure directories exist
ensure_directories()

def clear_review_folder():
    """Remove all files from the review folder."""
    review_dir = PDF_TXT_DIR / "needs_review"
    if review_dir.exists():
        for f in review_dir.glob("*.txt"):
            try:
                f.unlink()
            except OSError as e:
                logger.error(f"Error deleting review file {f}: {e}")

def get_cache_path(pdf_path):
    """Get the path to the cache file for a PDF."""
    try:
        return CACHE_DIR / f"{pdf_path.stem}_{pdf_path.stat().st_size}.json"
    except (FileNotFoundError, OSError):
        return CACHE_DIR / f"{pdf_path.stem}_unknown.json"

def process_single_pdf(pdf_path, progress_queue, ignore_cache=False):
    """Process a single PDF file and extract its data."""
    # Ensure pdf_path is a Path object
    pdf_path = Path(pdf_path)
    filename = pdf_path.name
    cache_path = get_cache_path(pdf_path)

    # Provide feedback about which file is being processed
    logger.info(f"Processing: {filename}")
    progress_queue.put({"type": "log", "tag": "info", "msg": f"Processing: {filename}"})
    
    # Check cache first unless ignore_cache is True
    if not ignore_cache and cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            if "status" not in cached_data:
                raise KeyError("Invalid cache data format")
            
            progress_queue.put({"type": "log", "tag": "info", "msg": f"Loaded from cache: {filename}"})
            
            # Handle review status
            if cached_data.get("status") == "Needs Review" and "review_info" in cached_data:
                progress_queue.put({"type": "review_item", "data": cached_data.get("review_info")})
            
            # Update counters
            progress_queue.put({"type": "file_complete", "status": cached_data.get("status")})
            if cached_data.get("ocr_used"):
                progress_queue.put({"type": "increment_counter", "counter": "ocr"})
            
            return cached_data
        except (json.JSONDecodeError, KeyError) as e:
            progress_queue.put({"type": "log", "tag": "warning", "msg": f"Corrupt cache for {filename}. Reprocessing..."})
            logger.warning(f"Cache error for {filename}: {e}")

    # Process the PDF
    progress_queue.put({"type": "status", "msg": f"Checking: {filename}", "led": "Queued"})
    
    # Check if OCR is needed
    try:
        absolute_pdf_path = str(pdf_path.resolve())
        ocr_required = _is_ocr_needed(absolute_pdf_path)
        
        if ocr_required:
            progress_queue.put({"type": "status", "msg": f"OCR: {filename}", "led": "OCR"})
            progress_queue.put({"type": "increment_counter", "counter": "ocr"})
        
        # Extract text
        progress_queue.put({"type": "status", "msg": f"Extracting text: {filename}", "led": "Processing"})
        extracted_text = extract_text_from_pdf(absolute_pdf_path)
        
        # Check if text extraction failed
        if not extracted_text or not extracted_text.strip():
            logger.warning(f"Text extraction failed for {filename}")
            progress_queue.put({"type": "log", "tag": "error", "msg": f"Text extraction failed for {filename}"})
            
            result = {
                "filename": filename,
                "models": "Error: Text Extraction Failed",
                "author": "",
                "status": "Fail",
                "ocr_used": ocr_required,
                "review_info": None
            }
            
            progress_queue.put({"type": "file_complete", "status": "Fail"})
            
            # Save to cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(result, f)
                
            return result
        
        # Harvest data
        progress_queue.put({"type": "status", "msg": f"Analyzing: {filename}", "led": "AI"})
        data = harvest_all_data(extracted_text, filename)
        
        # Determine status based on model extraction
        if data["models"] == "Not Found":
            status = "Needs Review"
            
            # Save text to review folder
            review_txt_path = PDF_TXT_DIR / "needs_review" / f"{pdf_path.stem}.txt"
            with open(review_txt_path, 'w', encoding='utf-8') as f:
                f.write(f"--- Filename: {filename} ---\n\n{extracted_text}")
            
            # Create review info
            review_info = {
                "filename": filename,
                "reason": "No models found",
                "txt_path": str(review_txt_path),
                "pdf_path": str(pdf_path)
            }
            
            # Update the queue
            progress_queue.put({"type": "review_item", "data": review_info})
            progress_queue.put({"type": "log", "tag": "warning", "msg": f"No models found in {filename}, saved for review"})
        else:
            status = "Pass"
            review_info = None
            progress_queue.put({"type": "log", "tag": "success", "msg": f"Found models in {filename}: {data['models']}"})
        
        # Create result
        result = {
            "filename": filename,
            **data,
            "status": status,
            "ocr_used": ocr_required,
            "review_info": review_info
        }
        
        # Save to cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(result, f)
        
        # Update the queue
        progress_queue.put({"type": "file_complete", "status": result["status"]})
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing {filename}: {e}\n{traceback.format_exc()}")
        progress_queue.put({"type": "log", "tag": "error", "msg": f"Error processing {filename}: {e}"})
        
        # Create error result
        result = {
            "filename": filename,
            "models": f"Error: {type(e).__name__}",
            "author": "",
            "status": "Fail",
            "ocr_used": False,
            "review_info": None
        }
        
        # Update the queue
        progress_queue.put({"type": "file_complete", "status": "Fail"})
        
        # Save to cache
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(result, f)
        except Exception:
            pass
            
        return result

def run_processing_job(job_info, progress_queue, cancel_event, pause_event):
    """Main processing job wrapper calling :func:`process_job`."""
    events = {
        "progress_queue": progress_queue,
        "cancel_event": cancel_event,
        "pause_event": pause_event,
    }
    job = dict(job_info)
    job.update(events)
    process_job(job, events)

def _fetch(job):
    return fetch_data(job)


def _parse(data):
    return parse_data(data)


def _export(parsed, job):
    export_results(parsed, job)


def process_job(job, events):
    try:
        data = _fetch(job)
    except Exception as exc:
        logger.exception("Fetch step failed", exc_info=exc)
        return
    try:
        parsed = _parse(data)
    except Exception as exc:
        logger.exception("Parse step failed", exc_info=exc)
        return
    try:
        _export(parsed, job)
    except Exception as exc:
        logger.exception("Export step failed", exc_info=exc)


def _execute_job(job, log_cb, status_cb, success_cb, error_cb, is_cancelled):
    run_processing_job(job, queue.Queue(), threading.Event(), threading.Event())


def process_folder(folder_path, excel_path, log_cb, status_cb, success_cb, error_cb, is_cancelled):
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(folder_path)
    job = {"input_path": folder, "excel_path": Path(excel_path)}
    _execute_job(job, log_cb, status_cb, success_cb, error_cb, is_cancelled)


def process_zip_archive(zip_path, excel_path, log_cb, status_cb, success_cb, error_cb, is_cancelled):
    zip_path = Path(zip_path)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            temp_dir = tempfile.mkdtemp(prefix="kyo_qa_")
            zf.extractall(temp_dir)
    except zipfile.BadZipFile:
        raise
    process_folder(temp_dir, excel_path, log_cb, status_cb, success_cb, error_cb, is_cancelled)
    shutil.rmtree(temp_dir, ignore_errors=True)
