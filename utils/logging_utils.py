"""Logging utilities"""
import logging
from datetime import datetime


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with consistent formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_scan_event(scan_type: str, resource_count: int):
    """Log scan event for audit trail"""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "scan_type": scan_type,
        "resource_count": resource_count,
    }
    logger = setup_logger("audit")
    logger.info(f"Scan event: {event}")
    return event
