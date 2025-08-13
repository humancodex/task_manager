import logging
import sys
from typing import Dict, Any
from app.config import settings


def setup_logging() -> None:
    """Configure application logging with proper format and level"""
    
    # Define log format based on environment
    if settings.log_format == "json":
        # Structured JSON logging for production
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        # Human-readable format for development
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    loggers_config = {
        "app": settings.log_level.upper(),
        "app.middleware.logging": "INFO",  # Ensure our middleware logs appear
        "uvicorn.access": "WARNING",  # Reduce uvicorn noise
        "uvicorn.error": "INFO",
        "sqlalchemy.engine": "WARNING",  # Reduce SQL query noise
        "slowapi": "WARNING"
    }
    
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level))
    
    # Log configuration info
    app_logger = logging.getLogger("app.core.logging_config")
    app_logger.info(f"Logging configured - Level: {settings.log_level}, Format: {settings.log_format}")


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(name)