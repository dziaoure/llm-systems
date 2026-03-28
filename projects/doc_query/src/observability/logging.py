from __future__ import annotations

import logging
from pathlib import Path

from src.config import get_settings


def get_logger(name: str = 'docquery') -> logging.Logger:
    settings = get_settings()
    log_dir = settings.paths.logs_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.app.log_level.upper(), logging.INFO))

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )

    file_handler = logging.FileHandler(log_dir / 'docquery.log', encoding='utf-8')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger

