"""
FILENAME: logging.py
DESCRIPTION/PURPOSE: Comprehensive logging configuration for AI Marketing Campaign Post Generator backend
Author: JP + 2025-06-18

This module provides centralized logging configuration with:
- DEBUG level logging to files
- Console logging for development
- Proper log formatting with timestamps
- File rotation and cleanup
- Environment-based configuration
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

# Default log configuration
DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_FILE = "logs/backend-debug.log"
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5

class AppLogger:
    """Comprehensive application logger for AI Marketing Campaign Post Generator."""
    
    def __init__(self, name: str = "ai_marketing_campaign"):
        self.name = name
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup comprehensive logging configuration."""
        # Get configuration from environment
        log_level = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
        log_file = os.getenv("LOG_FILE", DEFAULT_LOG_FILE)
        log_format = os.getenv("LOG_FORMAT", DEFAULT_LOG_FORMAT)
        date_format = os.getenv("LOG_DATE_FORMAT", DEFAULT_DATE_FORMAT)
        
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(getattr(logging, log_level))
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        formatter = logging.Formatter(log_format, date_format)
        
        # Setup file logging
        self._setup_file_logging(log_file, formatter)
        
        # Setup console logging for development
        self._setup_console_logging(formatter)
        
        # Log startup message
        self.logger.info(f"AI Marketing Campaign Post Generator - Backend Logger Initialized")
        self.logger.info(f"Log Level: {log_level}")
        self.logger.info(f"Log File: {log_file}")
        self.logger.debug(f"Debug logging enabled - detailed logs will be captured")
    
    def _setup_file_logging(self, log_file: str, formatter: logging.Formatter):
        """Setup file logging with rotation."""
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create file handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=DEFAULT_MAX_BYTES,
                backupCount=DEFAULT_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            
            # Add startup header to log file
            if not log_path.exists() or log_path.stat().st_size == 0:
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(f"# AI Marketing Campaign Post Generator - Backend Debug Log\n")
                    f.write(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# Log Level: DEBUG\n")
                    f.write(f"# =========================================================\n\n")
            
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
    
    def _setup_console_logging(self, formatter: logging.Formatter):
        """Setup console logging for development."""
        try:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)  # Less verbose for console
            
            # Simpler format for console
            console_formatter = logging.Formatter(
                "%(levelname)s - %(name)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            
            self.logger.addHandler(console_handler)
            
        except Exception as e:
            print(f"Warning: Could not setup console logging: {e}")
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, *args, **kwargs)

# Global logger instance
_app_logger = None

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get the application logger instance."""
    global _app_logger
    
    if _app_logger is None:
        _app_logger = AppLogger(name or "ai_marketing_campaign")
    
    return _app_logger.get_logger()

def setup_logging():
    """Setup application logging (called from main.py)."""
    global _app_logger
    
    if _app_logger is None:
        _app_logger = AppLogger()
    
    return _app_logger.get_logger()

# Convenience functions
def debug(message: str, *args, **kwargs):
    """Log debug message using global logger."""
    get_logger().debug(message, *args, **kwargs)

def info(message: str, *args, **kwargs):
    """Log info message using global logger."""
    get_logger().info(message, *args, **kwargs)

def warning(message: str, *args, **kwargs):
    """Log warning message using global logger."""
    get_logger().warning(message, *args, **kwargs)

def error(message: str, *args, **kwargs):
    """Log error message using global logger."""
    get_logger().error(message, *args, **kwargs)

def critical(message: str, *args, **kwargs):
    """Log critical message using global logger."""
    get_logger().critical(message, *args, **kwargs)

def exception(message: str, *args, **kwargs):
    """Log exception with traceback using global logger."""
    get_logger().exception(message, *args, **kwargs) 