import logging
from logging.handlers import RotatingFileHandler
from .config import settings

LOG_FILE = "trendbot.log"

def configure_logger() -> logging.Logger:
    logger = logging.getLogger("trendbot")
    if logger.handlers:
        return logger

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)

    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fmt))
    logger.addHandler(console)

    return logger

logger = configure_logger()
