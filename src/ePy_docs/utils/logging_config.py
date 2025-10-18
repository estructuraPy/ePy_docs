"""
Logging configuration for ePy_docs.

Provides structured logging with different levels for development and production.
Follows Python logging best practices with appropriate formatters and handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with colors for console output.
    
    Colors are only applied when output is to a terminal (not when piped).
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors if terminal supports it."""
        if sys.stderr.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_style: str = "detailed"
) -> logging.Logger:
    """
    Configure logging for ePy_docs with appropriate handlers and formatters.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If provided, logs are written to file
        format_style: Format style ('simple', 'detailed', 'json')
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logging(level="DEBUG", format_style="detailed")
        >>> logger.info("Starting document generation")
        >>> logger.warning("Missing optional parameter")
        >>> logger.error("Invalid input format")
    """
    logger = logging.getLogger("ePy_docs")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Define formats
    formats = {
        'simple': '%(levelname)s: %(message)s',
        'detailed': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'json': '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    }
    
    format_string = formats.get(format_style, formats['detailed'])
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = ColoredFormatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler if requested
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "ePy_docs") -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__ of the module)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.debug("Processing table data")
    """
    return logging.getLogger(name)


# Module-level convenience functions
def log_operation(operation: str, **kwargs) -> None:
    """
    Log an operation with structured context.
    
    Args:
        operation: Name of the operation being performed
        **kwargs: Additional context to include in the log
        
    Example:
        >>> log_operation("generate_html", filename="report.html", pages=10)
    """
    logger = get_logger()
    context = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"{operation} - {context}")


def log_validation_error(param: str, expected: str, actual: str) -> None:
    """
    Log a validation error with details.
    
    Args:
        param: Parameter name that failed validation
        expected: Expected type/value
        actual: Actual type/value received
        
    Example:
        >>> log_validation_error("df", "DataFrame", "None")
    """
    logger = get_logger()
    logger.error(f"Validation failed: {param} expected {expected}, got {actual}")


def log_performance(operation: str, duration: float, **metrics) -> None:
    """
    Log performance metrics for an operation.
    
    Args:
        operation: Name of the operation
        duration: Time taken in seconds
        **metrics: Additional performance metrics
        
    Example:
        >>> import time
        >>> start = time.time()
        >>> # ... do work ...
        >>> log_performance("generate_pdf", time.time() - start, pages=5, tables=3)
    """
    logger = get_logger()
    metrics_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
    logger.info(f"Performance: {operation} took {duration:.3f}s - {metrics_str}")


# Default logger setup
_default_logger = setup_logging(level="INFO", format_style="simple")
