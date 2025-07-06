# run_state.py
# Version: 26.0.0
# Last modified: 2025-07-03
import json
import os
from config import CACHE_DIR

STATE_FILE = CACHE_DIR / 'run_state.json'


def get_run_count() -> int:
    """Get the number of times the application has been run."""
    try:
        # Ensure the cache directory exists
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        if not STATE_FILE.exists():
            return 0
            
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return int(data.get('run_count', 0))
    except Exception:
        return 0


def increment_run_count() -> int:
    """Increment the run counter and return the new value."""
    count = get_run_count() + 1
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'run_count': count}, f)
    except Exception:
        pass  # Fail silently if we can't save the state
    return count