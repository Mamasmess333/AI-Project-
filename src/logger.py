"""
Structured logging for the AI Music Recommender.
Writes JSON-formatted log entries to logs/recommender.log.
"""

import json
import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "recommender.log")


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str = "recommender") -> logging.Logger:
    _ensure_log_dir()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def log_event(logger: logging.Logger, event: str, data: dict):
    payload = {"event": event, "timestamp": datetime.utcnow().isoformat(), **data}
    logger.info(json.dumps(payload))
