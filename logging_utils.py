import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
from datetime import datetime
import traceback

# Try to import optional error tracking
try:
    from error_tracker import get_handler as get_sentry_handler
except ImportError:
    def get_sentry_handler():
        return None

from config import LOGS_DIR

# Constants
SESSION_LOG_FILE = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_session.log"
SUCCESS_LOG_FILE = LOGS_DIR / f"{datetime.now().strftime('%Y%m%d')}_SUCCESSlog.md"
FAIL_LOG_FILE = LOGS_DIR / f"{datetime.now().strftime('%Y%m%d')}_FAILlog.md"

# Dictionary to track which loggers have already been set up
_initialized_loggers = {}

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Sets up a logger with a rotating file handler and console output."""
    # FIXED: Check if we've already initialized this logger
    if name in _initialized_loggers:
        return _initialized_loggers[name]
        
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    # FIXED: If the logger already has handlers, we don't need to add more
    if logger.hasHandlers():
        _initialized_loggers[name] = logger
        return logger

    # Ensure the log directory exists before creating a log file
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"CRITICAL: Could not create log directory at {LOGS_DIR}. Error: {e}")
        # Fallback to a simple console logger if file logging fails
        ch = logging.StreamHandler()
        ch_format = logging.Formatter('%(levelname)s - [%(name)s] - %(message)s')
        ch.setFormatter(ch_format)
        logger.addHandler(ch)
        _initialized_loggers[name] = logger
        return logger

    # Console Handler for immediate feedback
    ch = logging.StreamHandler()
    ch_format = logging.Formatter('%(levelname)s - [%(name)s] - %(message)s')
    ch.setFormatter(ch_format)
    logger.addHandler(ch)

    # Module-specific file handler with rotation
    try:
        fh = RotatingFileHandler(
            LOGS_DIR / f"{name}.log", 
            maxBytes=1024*1024,  # 1MB
            backupCount=3
        )
        fh_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        fh.setFormatter(fh_format)
        logger.addHandler(fh)
    except Exception as e:
        logger.error(f"Failed to set up file handler: {e}")
    
    # Add session log handler (shared across all loggers)
    try:
        session_handler = RotatingFileHandler(
            SESSION_LOG_FILE,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=2
        )
        session_format = logging.Formatter('%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
        session_handler.setFormatter(session_format)
        logger.addHandler(session_handler)
    except Exception as e:
        logger.error(f"Failed to set up session log handler: {e}")
    
    # Add optional Sentry error handler if available
    sentry_handler = get_sentry_handler()
    if sentry_handler:
        logger.addHandler(sentry_handler)
    
    _initialized_loggers[name] = logger
    return logger

def log_info(logger, message):
    """Log an info message and optionally append to the success log."""
    logger.info(message)
    
    # Optionally append to the SUCCESS log file
    try:
        with open(SUCCESS_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"- **{timestamp}**: {message}\n")
    except Exception:
        # If we can't write to the success log, just continue
        pass

def log_error(logger, message, exc_info=False, notify=True):
    """
    Log an error message with optional exception info.
    
    Args:
        logger: The logger to use
        message: Error message to log
        exc_info: Whether to include exception traceback
        notify: Whether to notify external services (like Sentry)
    """
    if exc_info:
        logger.error(message, exc_info=exc_info)
        if notify:
            try:
                from error_reporter import report_error_to_ai
                report_error_to_ai(
                    Exception(message), 
                    {"filename": traceback.extract_stack()[-2].filename, 
                     "lineno": traceback.extract_stack()[-2].lineno}
                )
            except ImportError:
                pass  # Error reporter not available
    else:
        logger.error(message)
    
    # Append to the FAIL log file
    try:
        with open(FAIL_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"- **{timestamp}**: {message}\n")
    except Exception:
        # If we can't write to the fail log, just continue
        pass

def log_warning(logger, message):
    """Log a warning message."""
    logger.warning(message)