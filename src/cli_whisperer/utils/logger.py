"""
Comprehensive logging system for CLI Whisperer.

This module provides both console and file logging with rotation,
structured formatting, and debug capabilities for troubleshooting.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class CLIWhispererLogger:
    """Enhanced logger with console and file output."""
    
    def __init__(self, name: str = "cli_whisperer", debug_mode: bool = False):
        """
        Initialize the logger with both console and file handlers.
        
        Args:
            name (str): Logger name
            debug_mode (bool): Enable debug level logging to console
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.debug_mode = debug_mode
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create log directory
        self.log_dir = Path.home() / ".cli-whisperer"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "debug.log"
        
        # Setup handlers
        self._setup_file_handler()
        self._setup_console_handler()
        
        # Log startup
        self.info(f"CLI Whisperer Logger initialized - Debug mode: {debug_mode}")
        self.info(f"Log file: {self.log_file}")
    
    def _setup_file_handler(self):
        """Setup rotating file handler."""
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Detailed formatter for file
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """Setup console handler with appropriate level."""
        console_handler = logging.StreamHandler(sys.stdout)
        
        if self.debug_mode:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.WARNING)
        
        # Simple formatter for console
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, context: Optional[dict] = None):
        """Log debug message."""
        full_message = self._format_message(message, context)
        self.logger.debug(full_message)
    
    def info(self, message: str, context: Optional[dict] = None):
        """Log info message."""
        full_message = self._format_message(message, context)
        self.logger.info(full_message)
    
    def warning(self, message: str, context: Optional[dict] = None):
        """Log warning message."""
        full_message = self._format_message(message, context)
        self.logger.warning(full_message)
    
    def error(self, message: str, context: Optional[dict] = None, exc_info: bool = False):
        """Log error message."""
        full_message = self._format_message(message, context)
        self.logger.error(full_message, exc_info=exc_info)
    
    def critical(self, message: str, context: Optional[dict] = None, exc_info: bool = False):
        """Log critical message."""
        full_message = self._format_message(message, context)
        self.logger.critical(full_message, exc_info=exc_info)
    
    def _format_message(self, message: str, context: Optional[dict] = None) -> str:
        """Format message with optional context."""
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            return f"{message} | Context: {context_str}"
        return message
    
    def log_method_entry(self, method_name: str, **kwargs):
        """Log method entry with parameters."""
        params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.debug(f"→ Entering {method_name}({params})")
    
    def log_method_exit(self, method_name: str, result: any = None):
        """Log method exit with result."""
        if result is not None:
            self.debug(f"← Exiting {method_name} → {result}")
        else:
            self.debug(f"← Exiting {method_name}")
    
    def log_ui_operation(self, operation: str, widget_id: str, success: bool = True, error: str = None):
        """Log UI operations with context."""
        context = {"widget_id": widget_id, "success": success}
        if error:
            context["error"] = error
            self.error(f"UI Operation Failed: {operation}", context)
        else:
            self.debug(f"UI Operation: {operation}", context)
    
    def log_transcription_step(self, step: str, details: dict = None):
        """Log transcription process steps."""
        context = {"step": step}
        if details:
            context.update(details)
        self.info(f"Transcription Step: {step}", context)


# Global logger instance
_logger_instance: Optional[CLIWhispererLogger] = None

def get_logger(debug_mode: bool = False) -> CLIWhispererLogger:
    """Get or create global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        # Check for debug mode environment variable
        debug_env = os.getenv("CLI_WHISPERER_DEBUG", "false").lower() == "true"
        _logger_instance = CLIWhispererLogger(debug_mode=debug_mode or debug_env)
    return _logger_instance

def enable_debug_mode():
    """Enable debug mode for existing logger."""
    global _logger_instance
    if _logger_instance:
        _logger_instance.debug_mode = True
        # Update console handler level
        for handler in _logger_instance.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
                handler.setLevel(logging.DEBUG)
        _logger_instance.info("Debug mode enabled")