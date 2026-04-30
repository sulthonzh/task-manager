import logging
import sys


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create and configure a logger with consistent formatting.

    Args:
        name: Logger name, typically __name__ of the calling module.
        level: Logging level, defaults to INFO.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
