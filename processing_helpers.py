import logging

logger = logging.getLogger(__name__)


def fetch_data(job):
    """Placeholder fetch step."""
    logger.info("Fetching job data")
    return job


def parse_data(data):
    """Placeholder parse step."""
    logger.info("Parsing data")
    return data


def export_results(parsed, job):
    """Placeholder export step."""
    logger.info("Exporting results")
    return None
