from typing import Any, Dict, List, Optional
"""Logging infrastructure - Implements LoggerPort from domain."""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from app.domain.ports import LoggerPort

from .config import Settings


class LoggerAdapter(LoggerPort):
    """
    Logger adapter implementing LoggerPort.
    
    Wraps Python's logging module to implement domain's logging interface.
    Uses JSON formatting for production, human-readable for development.
    """
    
    def __init__(self, name: str, request_id: Optional[str] = None):
        """
        Initialize logger adapter.
        
        Args:
            name: Logger name (usually module name)
            request_id: Optional request ID for correlation
        """
        self._logger = logging.getLogger(name)
        self._request_id = request_id
    
    def _add_context(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Add request context to log kwargs."""
        if self._request_id:
            kwargs["request_id"] = self._request_id
        return kwargs
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(message, extra=self._add_context(kwargs))
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(message, extra=self._add_context(kwargs))
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(message, extra=self._add_context(kwargs))
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self._logger.error(message, extra=self._add_context(kwargs))
    
    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with stack trace."""
        self._logger.exception(message, extra=self._add_context(kwargs))


def setup_logging(settings: Settings) -> None:
    """
    Configure logging for the application.
    
    Args:
        settings: Application settings
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Choose formatter based on environment
    if settings.is_production:
        # JSON formatter for production (machine-readable)
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # Human-readable formatter for development
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def get_logger(name: str, request_id: Optional[str] = None) -> LoggerPort:
    """
    Get logger instance.
    
    Args:
        name: Logger name (usually __name__)
        request_id: Optional request ID for correlation
        
    Returns:
        LoggerPort implementation
    """
    return LoggerAdapter(name, request_id)
