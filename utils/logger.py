"""
Logger for Roastify Bot - Termux Compatible
Fixed with proper logger export
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Try to import coloredlogs (optional)
try:
    import coloredlogs
    HAS_COLOREDLOGS = True
except ImportError:
    HAS_COLOREDLOGS = False

# Fix encoding for Termux/Android
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

class Logger:
    """লগার ক্লাস - সম্পূর্ণ ফিক্সড"""
    
    _instance = None
    
    def __new__(cls, name="RoastifyBot"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(name)
        return cls._instance
    
    def _initialize(self, name):
        """লগার ইনিশিয়ালাইজ করে"""
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Set level
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory
        self._setup_logs_directory()
        
        # Setup handlers
        self._setup_handlers()
        
        # Install colored logs if available
        if HAS_COLOREDLOGS:
            self._setup_colored_logs()
        
        # Log initialization
        self.logger.info(f"Logger initialized for {name}")
    
    def _setup_logs_directory(self):
        """লগস ডিরেক্টরি সেটআপ করে"""
        logs_dir = Path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create today's log file
        today = datetime.now().strftime("%Y%m%d")
        self.today_log_file = logs_dir / f"roastify_{today}.log"
    
    def _setup_handlers(self):
        """লগ হ্যান্ডলার সেটআপ করে"""
        # File handler with UTF-8 encoding
        try:
            file_handler = logging.FileHandler(
                self.today_log_file,
                encoding='utf-8',
                mode='a'
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter for file
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create file handler: {e}")
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter for console
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def _setup_colored_logs(self):
        """কলার্ড লগস সেটআপ করে"""
        try:
            coloredlogs.install(
                level='INFO',
                logger=self.logger,
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        except Exception as e:
            self.logger.warning(f"Colored logs not available: {e}")
    
    def get_logger(self):
        """লগার অবজেক্ট রিটার্ন করে"""
        return self.logger

# Create global logger instance
_logger_instance = Logger()
logger = _logger_instance.get_logger()

# Convenience functions
def get_logger(name=None):
    """লগার পেতে হেল্পার ফাংশন"""
    if name:
        return Logger(name).get_logger()
    return logger

def log_info(message, **kwargs):
    """ইনফো লগ করে"""
    logger.info(message, **kwargs)

def log_error(message, **kwargs):
    """এরর লগ করে"""
    logger.error(message, **kwargs)

def log_warning(message, **kwargs):
    """ওয়ার্নিং লগ করে"""
    logger.warning(message, **kwargs)

def log_debug(message, **kwargs):
    """ডিবাগ লগ করে"""
    logger.debug(message, **kwargs)

# Export everything
__all__ = [
    'logger',
    'get_logger',
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'Logger'
]

# Test if run directly
if __name__ == "__main__":
    logger.info("Logger test started")
    logger.info("বাংলা টেস্ট: লগার কাজ করছে!")
    print(f"✅ Logger is working! Log file: {_logger_instance.today_log_file}")
