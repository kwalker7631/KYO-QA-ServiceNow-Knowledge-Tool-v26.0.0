# processing_engine.py
import shutil
import time
import json
import logging
from pathlib import Path
from datetime import datetime
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("processing_engine")

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
    """Main processing job that handles multiple PDFs and updates Excel."""
    try:
        # Extract job info
        is_rerun = job_info.get("is_rerun", False)
        excel_path = Path(job_info["excel_path"])
        input_path = job_info["input_path"]
        
        # Log job start
        logger.info("Processing job started")
        progress_queue.put({"type": "log", "tag": "info", "msg": "Processing job started."})

        # Handle rerun vs new run
        if is_rerun:
            # For reruns, use the existing Excel file
            cloned_path = excel_path
            clear_review_folder()
        else:
            # For new runs, create a clone of the Excel file
            ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            cloned_path = OUTPUT_DIR / f"cloned_{excel_path.stem}_{ts}{excel_path.suffix}"
            
            # Check if the Excel file is locked
            if is_file_locked(excel_path):
                error_msg = "Input Excel is locked. Close it and try again."
                logger.error(error_msg)
                progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
                progress_queue.put({"type": "finish", "status": "Error"})
                return
                
            # Copy the Excel file
            try:
                shutil.copy(excel_path, cloned_path)
                progress_queue.put({"type": "log", "tag": "info", "msg": f"Created copy of Excel file: {cloned_path.name}"})
            except Exception as e:
                error_msg = f"Failed to copy Excel file: {e}"
                logger.error(error_msg)
                progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
                progress_queue.put({"type": "finish", "status": "Error"})
                return
        
        # Get list of files to process
        files = []
        if isinstance(input_path, list):
            # Input is a list of files
            files = [Path(f) for f in input_path if Path(f).suffix.lower() == '.pdf']
        else:
            # Input is a directory
            try:
                input_dir = Path(input_path)
                if input_dir.exists():
                    files = list(input_dir.glob('*.pdf'))
                else:
                    error_msg = f"Input directory does not exist: {input_dir}"
                    logger.error(error_msg)
                    progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
                    progress_queue.put({"type": "finish", "status": "Error"})
                    return
            except Exception as e:
                error_msg = f"Failed to read input directory: {e}"
                logger.error(error_msg)
                progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
                progress_queue.put({"type": "finish", "status": "Error"})
                return
        
        # Log number of files found
        progress_queue.put({"type": "log", "tag": "info", "msg": f"Found {len(files)} PDF files to process"})
        
        if not files:
            progress_queue.put({"type": "log", "tag": "warning", "msg": "No PDF files found"})
            progress_queue.put({"type": "finish", "status": "Complete"})
            return
        
        # Process each file
        results = {}
        for i, path in enumerate(files):
            # Check for cancellation
            if cancel_event.is_set():
                progress_queue.put({"type": "log", "tag": "warning", "msg": "Processing cancelled"})
                progress_queue.put({"type": "finish", "status": "Cancelled"})
                return
            
            # Handle pause
            if pause_event and pause_event.is_set():
                progress_queue.put({"type": "status", "msg": "Paused", "led": "Paused"})
                while pause_event.is_set() and not cancel_event.is_set():
                    time.sleep(0.5)
                if cancel_event.is_set():
                    progress_queue.put({"type": "log", "tag": "warning", "msg": "Processing cancelled"})
                    progress_queue.put({"type": "finish", "status": "Cancelled"})
                    return
            
            # Update progress
            progress_queue.put({"type": "progress", "current": i + 1, "total": len(files)})
            
            # Process the file
            res = process_single_pdf(path, progress_queue, ignore_cache=is_rerun)
            if res:
                results[res["filename"]] = res

        # Check for cancellation before Excel update
        if cancel_event.is_set():
            progress_queue.put({"type": "finish", "status": "Cancelled"})
            return

        # Update Excel file
        progress_queue.put({"type": "status", "msg": "Updating Excel...", "led": "Saving"})
        
        if not OPENPYXL_AVAILABLE:
            error_msg = "Excel processing not available (openpyxl not installed)"
            logger.error(error_msg)
            progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
            progress_queue.put({"type": "finish", "status": "Error"})
            return
        
        try:
            # Open the Excel file
            workbook = openpyxl.load_workbook(cloned_path)
            sheet = workbook.active
            
            # Get headers
            headers = [str(c.value).lower() if c.value else "" for c in sheet[1]]
            
            # Add status column if it doesn't exist
            status_col_name = STATUS_COLUMN_NAME.lower()
            if status_col_name not in headers:
                sheet.cell(row=1, column=len(headers) + 1).value = STATUS_COLUMN_NAME
                headers.append(status_col_name)
            
            # Get column indices (case-insensitive)
            cols = {}
            for name, lookup in [
                (DESCRIPTION_COLUMN_NAME, 'short description'),
                (META_COLUMN_NAME, 'meta'),
                (AUTHOR_COLUMN_NAME, 'author'),
                (STATUS_COLUMN_NAME, 'processing status')
            ]:
                try:
                    cols[name] = headers.index(lookup.lower()) + 1
                except ValueError:
                    # If column not found, try the exact name
                    try:
                        cols[name] = headers.index(name.lower()) + 1
                    except ValueError:
                        error_msg = f"Column '{name}' not found in Excel file"
                        logger.error(error_msg)
                        progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
                        # Don't return, try to continue with available columns
            
            # Check if required columns were found
            if DESCRIPTION_COLUMN_NAME not in cols or META_COLUMN_NAME not in cols:
                error_msg = f"Required columns missing: needs at least '{DESCRIPTION_COLUMN_NAME}' and '{META_COLUMN_NAME}'"
                logger.error(error_msg)
                progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
                progress_queue.put({"type": "finish", "status": "Error"})
                return
                
            # Define cell styles
            fills = {
                "Pass": PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),
                "Fail": PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
                "Needs Review": PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid"),
                "OCR": PatternFill(start_color="DBE5F1", end_color="DBE5F1", fill_type="solid")
            }
            
            # Update rows
            updated_count = 0
            for row in sheet.iter_rows(min_row=2):
                desc_cell = row[cols[DESCRIPTION_COLUMN_NAME]-1]
                if not desc_cell.value:
                    continue
                    
                desc = str(desc_cell.value)
                for filename, data in results.items():
                    # Look for filename in description
                    if Path(filename).stem.lower() in desc.lower():
                        # Update meta column if it's empty
                        meta_cell = row[cols[META_COLUMN_NAME]-1]
                        if not meta_cell.value:
                            meta_cell.value = data["models"]
                            
                        # Update author column if available
                        if AUTHOR_COLUMN_NAME in cols and "author" in data:
                            author_cell = row[cols[AUTHOR_COLUMN_NAME]-1]
                            if not author_cell.value and data["author"]:
                                author_cell.value = data["author"]
                                
                        # Update status column if available
                        if STATUS_COLUMN_NAME in cols:
                            status_cell = row[cols[STATUS_COLUMN_NAME]-1]
                            status_cell.value = f"{data['status']}{' (OCR)' if data['ocr_used'] else ''}"
                            
                        updated_count += 1
                        break
                
            # Apply formatting
            progress_queue.put({"type": "status", "msg": "Applying formatting...", "led": "Saving"})
            
            # Apply cell styles
            for row in sheet.iter_rows(min_row=2):
                if STATUS_COLUMN_NAME in cols:
                    status_cell = row[cols[STATUS_COLUMN_NAME]-1]
                    if not status_cell.value:
                        continue
                        
                    status_val = str(status_cell.value)
                    fill_key = status_val.replace(" (OCR)", "").strip()
                    fill = fills.get(fill_key)
                    
                    if fill:
                        # Apply fill to the entire row
                        for cell in row:
                            cell.fill = fill
                            
                        # Override for OCR status
                        if "(OCR)" in status_val:
                            status_cell.fill = fills["OCR"]
            
            # Adjust column widths
            for i, col in enumerate(sheet.columns, 1):
                max_len = 0
                for cell in col:
                    if cell.value:
                        try:
                            cell_len = len(str(cell.value))
                            if cell_len > max_len:
                                max_len = cell_len
                        except Exception:
                            pass
                
                adjusted_width = min(max_len + 2, 60)  # Cap width at 60 characters
                sheet.column_dimensions[get_column_letter(i)].width = adjusted_width
            
            # Save the Excel file
            workbook.save(cloned_path)
            
            # Log success
            progress_queue.put({"type": "log", "tag": "success", "msg": f"Updated {updated_count} rows in Excel file"})
            progress_queue.put({"type": "result_path", "path": str(cloned_path)})
            progress_queue.put({"type": "finish", "status": "Complete"})
            
        except Exception as e:
            error_msg = f"Error updating Excel: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
            progress_queue.put({"type": "finish", "status": "Error"})

    except Exception as e:
        error_msg = f"Critical error in processing job: {e}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        progress_queue.put({"type": "log", "tag": "error", "msg": error_msg})
        progress_queue.put({"type": "finish", "status": f"Error: {type(e).__name__}"})