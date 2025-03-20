import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = "app.log", max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5, log_level: str = "INFO"):
    """Configure logging for the application.
    
    Args:
        log_file (str): Name of the log file
        max_bytes (int): Maximum size of each log file in bytes
        backup_count (int): Number of backup files to keep
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Define formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level))
    
    # Set up file handler
    log_path = log_dir / log_file
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(getattr(logging, log_level))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure app logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.DEBUG)
    
    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    
    return app_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name) 