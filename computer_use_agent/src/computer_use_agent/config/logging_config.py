"""Logging configuration for the agent system.

This module sets up structured logging following Python logging best practices.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[Path] = None,
    enable_console: bool = True,
) -> None:
    """Configure logging for the application.

    Sets up both file and console logging with appropriate formatting.
    Following Python logging best practices with named loggers.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to write logs to a file.
        enable_console: Whether to enable console output.
    """
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    simple_formatter = logging.Formatter(
        fmt='%(levelname)s: %(message)s',
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file is not None:
        # Ensure parent directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)

    # Set level for the agent package
    logging.getLogger('computer_use_agent').setLevel(level)

    logging.info('Logging configured successfully')
