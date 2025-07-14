# processing_helpers.py
# Version: 2.0.0
# Last modified: 2025-07-13

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from config import CACHE_DIR, OUTPUT_DIR
from data_harvesters import harvest_all_data
from excel_generator import ExcelGenerator
from ocr_utils import extract_text_from_pdf
from app_state import AppState

logger = logging.getLogger(__name__)


def fetch_data(job: Dict[str, Any], app_state: AppState) -> List[Dict[str, Any]]:
    """Fetches data from PDF files, using OCR if necessary."""
    input_path = job["input_path"]
    results = []

    if isinstance(input_path, list):
        files_to_process = input_path
    elif isinstance(input_path, Path) and input_path.is_dir():
        files_to_process = list(input_path.glob("**/*.pdf"))
    else:
        logger.error(f"Invalid input path: {input_path}")
        return []

    total_files = len(files_to_process)
    for i, pdf_path in enumerate(files_to_process):
        if app_state.is_cancelled():
            break
        
        app_state.check_pause()
        if app_state.is_cancelled():
            break

        app_state.update_status(f"Processing {pdf_path.name}...")
        try:
            text, ocr_used = extract_text_from_pdf(str(pdf_path), use_ocr=True)
            if ocr_used:
                app_state.log(f"OCR was used for {pdf_path.name}", "info")
                app_state.increment_ocr_counter()

            # The harvest_all_data function now returns a complete dictionary
            data = harvest_all_data(text, pdf_path.name)
            results.append(data)
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}", exc_info=True)
            results.append(
                {"filename": pdf_path.name, "status": "Fail", "error": str(e)}
            )
        app_state.update_progress((i + 1) / total_files * 100)
    return results


def parse_data(
    raw_data: List[Dict[str, Any]], app_state: AppState
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Parses the raw harvested data, assigns a status, and categorizes the results.
    This logic now correctly determines the status for each file.
    """
    logger.info("Parsing and validating harvested data...")
    passed_items = []
    review_items = []

    for item in raw_data:
        # If an error occurred during fetching, it's a failure.
        if item.get("status") == "Fail":
            review_items.append(item)
        # If no models were found, it needs review.
        elif not item.get("models"):
            item["status"] = "Needs Review"
            item["review_reason"] = "No device models were found."
            review_items.append(item)
            app_state.add_review_item(item)
        # Otherwise, it's a pass.
        else:
            item["status"] = "Pass"
            passed_items.append(item)
        
        # This ensures the UI counters are updated for every file.
        app_state.update_counts(item["status"])

    return passed_items, review_items


def export_to_excel(
    results: List[Dict[str, Any]], excel_template: Path, app_state: AppState
) -> Tuple[Path, List[str]]:
    """Generates an Excel report from the results."""
    output_filename = OUTPUT_DIR / f"output_{app_state.get_timestamp()}.xlsx"
    
    generator = ExcelGenerator(str(excel_template))
    output_path, skipped_files = generator.create_report(
        results, str(output_filename)
    )
    return output_path, skipped_files
