import logging
from logging_utils import setup_logger

def configure_logging(name: str = 'app', level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger using logging_utils.setup_logger."""
    return setup_logger(name, level)
