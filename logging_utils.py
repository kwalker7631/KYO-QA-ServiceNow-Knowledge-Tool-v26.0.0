import logging
from logging_config import configure_logging


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    return configure_logging(name, level)
