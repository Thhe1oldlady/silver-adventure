"""Logging configuration for Silver Adventure."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from .config import get_config


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """Setup logging configuration."""
    config = get_config()
    
    # Use config values if not provided
    level = level or config.log_level
    log_file = log_file or config.log_file
    
    # Default format
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class PipelineLogger:
    """Specialized logger for pipeline operations."""
    
    def __init__(self, name: str, extra_context: Optional[Dict[str, Any]] = None):
        self.logger = get_logger(name)
        self.extra_context = extra_context or {}
    
    def _log(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log message with optional extra context."""
        context = {**self.extra_context}
        if extra:
            context.update(extra)
        
        getattr(self.logger, level)(message, extra=context)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log("debug", message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log("info", message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log("warning", message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log("error", message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log("critical", message, kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception message."""
        self._log("exception", message, kwargs)
    
    def pipeline_start(self, pipeline_name: str, **kwargs):
        """Log pipeline start."""
        self.info(f"Pipeline '{pipeline_name}' started", pipeline_name=pipeline_name, **kwargs)
    
    def pipeline_end(self, pipeline_name: str, success: bool = True, **kwargs):
        """Log pipeline end."""
        status = "completed successfully" if success else "failed"
        self.info(f"Pipeline '{pipeline_name}' {status}", 
                 pipeline_name=pipeline_name, success=success, **kwargs)
    
    def step_start(self, step_name: str, **kwargs):
        """Log step start."""
        self.info(f"Step '{step_name}' started", step_name=step_name, **kwargs)
    
    def step_end(self, step_name: str, success: bool = True, **kwargs):
        """Log step end."""
        status = "completed" if success else "failed"
        self.info(f"Step '{step_name}' {status}", 
                 step_name=step_name, success=success, **kwargs)
    
    def performance_metric(self, metric_name: str, value: float, **kwargs):
        """Log performance metric."""
        self.info(f"Performance metric '{metric_name}': {value}", 
                 metric_name=metric_name, metric_value=value, **kwargs)


# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()