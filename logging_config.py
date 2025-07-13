import logging


def configure_logging(name: str = 'app', level: int = logging.INFO) -> logging.Logger:
    """Simple logger configuration used during testing."""
    logger = logging.getLogger(name)
    logger.propagate = False
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
