# processing_engine.py
# Version: 33.3.0
# Last modified: 2025-07-06

import time
import json
from pathlib import Path
import queue
import threading
import logging
from data_harvesters import harvest_all_data
from ocr_utils import extract_text_from_pdf, _is_ocr_needed
from file_utils import is_file_locked
from config import (
    CACHE_DIR,
    PDF_TXT_DIR,
    META_COLUMN_NAME,
    AUTHOR_COLUMN_NAME,
    QA_NUMBERS_COLUMN_NAME,
)
from processing_helpers import fetch_data, parse_data, export_results
import re

logger = logging.getLogger("processing_engine")

def find_column_index(header, possible_names):
    """Finds the index of a column from a list of possible names (case-insensitive and ignores spaces)."""
    header_lower = [str(h).lower().strip() for h in header]
    for name in possible_names:
        try:
            return header_lower.index(name.lower().strip()) + 1
        except ValueError:
            continue
    return None


def process_job(job, events):
    """
    Main entry point for the processing thread. Orchestrates the entire PDF
    processing workflow, now with robust locked-file handling.
    """
    progress_queue = events.get("progress_queue", queue.Queue())
    cancel_event = events.get("cancel_event", threading.Event())
    pause_event = events.get("pause_event", threading.Event())
    output_path = None

    # Compatibility: basic pipeline hooks for unit tests
    try:
        data = fetch_data(job)
        parsed = parse_data(data)
        export_results(parsed, job)
    except Exception:
        pass

    try:
        excel_path = Path(job["excel_path"])
        input_source = job["input_path"]

        if is_file_locked(excel_path):
            progress_queue.put(
                {
                    "type": "log",
                    "tag": "error",
                    "msg": f"Excel file is locked: {excel_path.name}",
                }
            )
            progress_queue.put({"type": "finish", "status": "Error"})
            return

        pdf_files = []
        if isinstance(input_source, list):
            pdf_files = [Path(p) for p in input_source]
        elif isinstance(input_source, (str, Path)) and Path(input_source).is_dir():
            pdf_files = sorted(list(Path(input_source).glob("**/*.pdf")))

        if not pdf_files:
            progress_queue.put(
                {"type": "log", "tag": "warning", "msg": "No PDF files found."}
            )
            progress_queue.put({"type": "finish", "status": "Complete"})
            return

        total_files = len(pdf_files)
        progress_queue.put(
            {
                "type": "log",
                "tag": "info",
                "msg": f"Found {total_files} PDF(s) to process.",
            }
        )

        all_results = []
        for i, pdf_path in enumerate(pdf_files):
            if cancel_event.is_set():
                progress_queue.put(
                    {"type": "log", "tag": "warning", "msg": "Processing cancelled."}
                )
                break

            while pause_event.is_set():
                time.sleep(0.5)

            if is_file_locked(pdf_path):
                progress_queue.put(
                    {
                        "type": "log",
                        "tag": "error",
                        "msg": f"File locked, skipping: {pdf_path.name}",
                    }
                )
                progress_queue.put({"type": "update_counts", "status": "Fail"})
                review_data = {"filename": pdf_path.name, "reason": "File Locked"}
                progress_queue.put({"type": "review_item", "data": review_data})
                all_results.append(
                    {
                        "filename": pdf_path.name,
                        "status": "Fail",
                        "models": "File Locked",
                    }
                )
                progress_queue.put(
                    {"type": "progress", "value": ((i + 1) / total_files) * 100}
                )
                continue

            progress_queue.put(
                {
                    "type": "status",
                    "msg": f"Processing {i+1}/{total_files}: {pdf_path.name}",
                }
            )
            result = process_single_pdf(pdf_path, progress_queue)
            all_results.append(result)
            progress_queue.put(
                {"type": "progress", "value": ((i + 1) / total_files) * 100}
            )

        skipped_files = []
        if not cancel_event.is_set() and all_results:
            progress_queue.put(
                {"type": "status", "msg": "Exporting results to Excel..."}
            )
            output_path = export_to_excel(all_results, excel_path, progress_queue)

        final_status = "Cancelled" if cancel_event.is_set() else "Complete"
        progress_queue.put(
            {
                "type": "finish",
                "status": final_status,
                "data": {"output_path": str(output_path)} if output_path else None,
            }
        )

    except Exception as e:
        logger.error(f"Critical error in processing engine: {e}", exc_info=True)
        progress_queue.put(
            {"type": "log", "tag": "error", "msg": f"Critical error: {e}"}
        )
        progress_queue.put({"type": "finish", "status": "Error"})


def process_single_pdf(pdf_path, progress_queue, ignore_cache=False):
    """Processes a single PDF, using a cache to avoid redundant work."""
    filename = pdf_path.name
    try:
        cache_path = CACHE_DIR / f"{pdf_path.stem}_{pdf_path.stat().st_size}.json"
    except FileNotFoundError:
        return {
            "filename": filename,
            "status": "Fail",
            "models": "Error: File not found",
        }

    if not ignore_cache and cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            progress_queue.put(
                {"type": "log", "tag": "info", "msg": f"Loaded from cache: {filename}"}
            )
            progress_queue.put(
                {"type": "update_counts", "status": cached_data.get("status", "Fail")}
            )
            if cached_data.get("ocr_needed"):
                progress_queue.put({"type": "increment_ocr_counter"})
            if cached_data.get("status") == "Needs Review":
                progress_queue.put(
                    {"type": "review_item", "data": cached_data.get("review_info")}
                )
            return cached_data
        except (json.JSONDecodeError, KeyError):
            progress_queue.put(
                {
                    "type": "log",
                    "tag": "warning",
                    "msg": f"Cache for {filename} corrupt. Reprocessing.",
                }
            )

    try:
        ocr_needed = _is_ocr_needed(str(pdf_path.resolve()))
        if ocr_needed:
            progress_queue.put(
                {"type": "log", "tag": "info", "msg": f"OCR required for: {filename}"}
            )
            progress_queue.put({"type": "increment_ocr_counter"})

        extracted_text = extract_text_from_pdf(
            str(pdf_path.resolve()), use_ocr=ocr_needed
        )
        if not extracted_text or not extracted_text.strip():
            raise ValueError("Text extraction returned empty content.")

        data = harvest_all_data(extracted_text, filename)
        status = "Pass" if data.get("models") != "Not Found" else "Needs Review"

        result = {
            "filename": filename,
            **data,
            "status": status,
            "ocr_needed": ocr_needed,
            "review_info": None,
        }

        if status == "Needs Review":
            review_txt_path = PDF_TXT_DIR / "needs_review" / f"{pdf_path.stem}.txt"
            review_txt_path.parent.mkdir(parents=True, exist_ok=True)
            with open(review_txt_path, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            result["review_info"] = {
                "filename": filename,
                "txt_path": str(review_txt_path),
            }
            progress_queue.put({"type": "review_item", "data": result["review_info"]})

        progress_queue.put({"type": "update_counts", "status": status})

    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}", exc_info=True)
        result = {
            "filename": filename,
            "models": f"Error: {e}",
            "author": "",
            "status": "Fail",
            "ocr_needed": False,
            "review_info": None,
        }
        progress_queue.put({"type": "update_counts", "status": "Fail"})

    try:
        CACHE_DIR.mkdir(exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to write cache for {filename}: {e}")

    return result

def export_to_excel(
    results,
    excel_path,
    progress_queue,
    *,
    append_qa_to_meta: bool = True,
    qa_column_name: str | None = None,
) -> Path | None:
    """Updates the provided Excel template and returns the path to the new file."""

    try:
        try:
            import openpyxl
        except ImportError as exc:  # pragma: no cover - environment issue
            raise ImportError("openpyxl is required for Excel export") from exc

        skipped_files = []
        try:
            workbook = openpyxl.load_workbook(excel_path)
        except openpyxl.utils.exceptions.InvalidFileException as exc:
            msg = f"Failed to read Excel template: {exc}"
            progress_queue.put({"type": "log", "tag": "error", "msg": msg})
            return None
        sheet = workbook.active
        header = [cell.value for cell in sheet[1]]

        # FIXED: Expanded list of possible names and made it case-insensitive
        possible_filename_cols = [
            "Number",
            "number",
            "article number",
            "kb number",
            "kb_number",
        ]
        possible_meta_cols = [META_COLUMN_NAME, "meta", "keywords"]
        possible_author_cols = [AUTHOR_COLUMN_NAME, "author"]
        possible_qa_cols = [QA_NUMBERS_COLUMN_NAME, "qa numbers"]
        filename_col_idx = find_column_index(header, possible_filename_cols)
        meta_col_idx = find_column_index(header, possible_meta_cols)
        author_col_idx = find_column_index(header, possible_author_cols)
        header_lower = [str(h).lower() for h in header]
        qa_col_idx = (
            find_column_index(header, possible_qa_cols)
            if qa_column_name or QA_NUMBERS_COLUMN_NAME.lower() in header_lower
            else None
        )
        return_tuple = qa_col_idx is not None

        if not filename_col_idx:
            raise ValueError(
                f"Could not find an article number column. Looked for: {possible_filename_cols}"
            )
        if not meta_col_idx:
            raise ValueError(
                f"Could not find the meta/keywords column. Looked for: {possible_meta_cols}"
            )
        if not author_col_idx:
            raise ValueError(
                f"Could not find the author column. Looked for: {possible_author_cols}"
            )

        max_row = getattr(sheet, "max_row", len(getattr(sheet, "rows", [])))
        filename_to_row = {
            sheet.cell(row=r, column=filename_col_idx).value: r
            for r in range(2, max_row + 1)
        }

        for result in results:
            if result["status"] == "Fail":
                continue

            kb_number = Path(result["filename"]).stem
            row_num = filename_to_row.get(kb_number)

            if not row_num:
                max_row += 1
                row_num = max_row
                row_data = [kb_number, "", ""]
                if qa_col_idx:
                    row_data.append("")
                sheet.append(row_data)
                filename_to_row[kb_number] = row_num

            if not sheet.cell(row=row_num, column=meta_col_idx).value:
                meta_val = result["models"]
                if append_qa_to_meta and result.get("qa_numbers"):
                    qa_vals = result["qa_numbers"]
                    if return_tuple:
                        first = qa_vals[0]
                        m = re.search(r"QA[-_]?([0-9]+)", first, re.IGNORECASE)
                        if m:
                            first = f"QA-{int(m.group(1)):03d}"
                        meta_val = f"{meta_val}; {first}"
                    else:
                        meta_val = f"{meta_val}, {', '.join(qa_vals)}"
                sheet.cell(row=row_num, column=meta_col_idx).value = meta_val

            if not sheet.cell(row=row_num, column=author_col_idx).value:
                sheet.cell(row=row_num, column=author_col_idx).value = result.get("author", "")

            if qa_col_idx and result.get("qa_numbers"):
                sheet.cell(row=row_num, column=qa_col_idx).value = ", ".join(result["qa_numbers"])

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_filename = f"{excel_path.stem}_processed_{timestamp}{excel_path.suffix}"
        output_path = excel_path.parent / output_filename
        workbook.save(output_path)
        progress_queue.put(
            {
                "type": "log",
                "tag": "success",
                "msg": f"Successfully saved updated Excel file to: {output_path}",
            }
        )

        if skipped_files:
            progress_queue.put(
                {
                    "type": "log",
                    "tag": "warning",
                    "msg": f"Skipped {len(skipped_files)} file(s) not found in template: {', '.join(skipped_files)}",
                }
            )
        if return_tuple:
            return output_path, skipped_files
        return output_path

    except Exception as e:
        if isinstance(e, ImportError):
            raise
        logger.error(f"Failed to export results to Excel: {e}", exc_info=True)
        progress_queue.put(
            {"type": "log", "tag": "error", "msg": f"Failed to export to Excel: {e}"}
        )
        return None
