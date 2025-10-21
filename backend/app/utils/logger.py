"""
Logging Configuration
Centralized logging setup with structured logs
"""

import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging() -> None:
    """
    Configure application-wide logging
    Uses loguru for better log management
    """
    
    # Remove default logger
    logger.remove()
    
    # Console logging (colored, formatted)
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
    )
    
    # File logging (JSON format for parsing)
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.LOG_FILE,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        backtrace=True,
        diagnose=True,
    )
    
    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}")
    logger.info(f"Log file: {settings.LOG_FILE}")


# Initialize logging when module is imported
setup_logging()


# Export logger for use across application
__all__ = ["logger"]