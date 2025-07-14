# app_state.py
# Version: 1.0.0
# Last modified: 2025-07-13

import threading
import queue
import time
from typing import Any, Dict, Optional

class AppState:
    """
    Manages the state of a processing run, including progress, events, and communication with the UI.
    """
    def __init__(self, progress_queue: queue.Queue, cancel_event: threading.Event, pause_event: threading.Event):
        self.progress_queue = progress_queue
        self.cancel_event = cancel_event
        self.pause_event = pause_event
        self.timestamp = time.strftime("%Y%m%d-%H%M%S")

    def log(self, message: str, level: str = "info") -> None:
        """Sends a log message to the main thread."""
        self.progress_queue.put({"type": "log", "msg": message, "tag": level})

    def update_status(self, message: str) -> None:
        """Updates the current status message in the UI."""
        self.progress_queue.put({"type": "status", "msg": message})

    def update_progress(self, value: float) -> None:
        """Updates the progress bar value."""
        self.progress_queue.put({"type": "progress", "value": value})

    def update_counts(self, status: str) -> None:
        """Updates the Pass/Fail/Review counts."""
        self.progress_queue.put({"type": "update_counts", "status": status})

    def increment_ocr_counter(self) -> None:
        """Increments the OCR usage counter."""
        self.progress_queue.put({"type": "increment_ocr_counter"})

    def add_review_item(self, data: Dict[str, Any]) -> None:
        """Adds an item to the review list in the UI."""
        self.progress_queue.put({"type": "review_item", "data": data})

    def finish_run(self, status: str, output_path: Optional[str] = None) -> None:
        """Signals that the run has finished."""
        data = {"output_path": output_path} if output_path else {}
        self.progress_queue.put({"type": "finish", "status": status, "data": data})

    def is_cancelled(self) -> bool:
        """Checks if the cancellation event has been set."""
        return self.cancel_event.is_set()

    def check_pause(self) -> None:
        """Pauses execution if the pause event is set."""
        while self.pause_event.is_set():
            if self.is_cancelled():
                break
            self.update_status("Paused...")
            time.sleep(1)

    def get_timestamp(self) -> str:
        """Returns the timestamp for the current run."""
        return self.timestamp
