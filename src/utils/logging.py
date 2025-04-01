#!/usr/bin/env python3
"""
Logging Utilities

This module provides standardized logging functionality for the application.
"""

import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from typing import List, Optional


def configure_logging(
    logger_name: str,
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    log_format: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
) -> logging.Logger:
    """
    Configure a logger with console and optional file handlers.
    
    Args:
        logger_name: The name of the logger
        log_level: The logging level (default: INFO)
        log_to_file: Whether to log to a file (default: True)
        log_file: The log file path (default: based on logger_name)
        max_file_size: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
        log_format: The log message format (default: timestamp - level - name - message)
        
    Returns:
        logging.Logger: The configured logger
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if requested
    if log_to_file:
        # Use provided log file or create one based on logger name
        if log_file is None:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{logger_name}.log")
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_agent_logger(agent_name: str, log_level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger configured specifically for an agent.
    
    Args:
        agent_name: The name of the agent
        log_level: The logging level (default: INFO)
        
    Returns:
        logging.Logger: The configured logger for the agent
    """
    # Sanitize agent name for use in the log file name
    sanitized_name = agent_name.lower().replace(" ", "_")
    return configure_logging(
        logger_name=f"agent.{sanitized_name}",
        log_level=log_level,
        log_file=f"logs/{sanitized_name}_agent.log"
    )


def log_exception(
    logger: logging.Logger, 
    exception: Exception, 
    message: str = "An error occurred"
) -> None:
    """
    Log an exception with consistent formatting.
    
    Args:
        logger: Logger to use
        exception: Exception to log
        message: Optional message to include
    """
    error_cls = exception.__class__.__name__
    error_msg = str(exception)
    error_tb = traceback.format_exc()
    
    logger.error(f"{message}: {error_cls} - {error_msg}")
    logger.debug(f"Error traceback:\n{error_tb}") 