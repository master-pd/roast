"""
Logger for Roastify Bot
Fully Fixed with proper exports
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Fix encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

class Logger:
    """লগার ক্লাস"""
    
    def __init__(self, name="RoastifyBot"):
        self.logger = logging.getLogger(name)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Set level
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler
        today = datetime.now().strftime("%Y%m%d")
        log_file = logs_dir / f"roastify_{today}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log initialization
        self.logger.info(f"Logger initialized for {name}")
    
    def get_logger(self):
        return self.logger

# Create global logger instance
_logger = Logger()
logger = _logger.get_logger()

# Convenience functions
def log_info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def log_error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)

def log_warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def log_debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

# Export
__all__ = ['logger', 'log_info', 'log_error', 'log_warning', 'log_debug']
