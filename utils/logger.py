"""
Logger for Roastify Bot - Termux Compatible
Fixed encoding and file handling issues
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import coloredlogs

# Fix encoding for Termux/Android
try:
    # Set UTF-8 encoding for stdout/stderr
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

# Set locale for Bengali support
try:
    import locale
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')
except:
    pass

class CustomLogger:
    """কাস্টম লগার ক্লাস - Termux compatible"""
    
    def __init__(self, name="RoastifyBot"):
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
        
        # Install colored logs
        self._setup_colored_logs()
        
        # Log initialization
        self.logger.info(f"Logger initialized for {name}")
    
    def _setup_logs_directory(self):
        """লগস ডিরেক্টরি সেটআপ করে"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create today's log file
        today = datetime.now().strftime("%Y%m%d")
        self.today_log_file = logs_dir / f"roastify_{today}.log"
    
    def _setup_handlers(self):
        """লগ হ্যান্ডলার সেটআপ করে"""
        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler(
            self.today_log_file,
            encoding='utf-8',
            mode='a'
        )
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
    
    def _setup_colored_logs(self):
        """কলার্ড লগস সেটআপ করে"""
        try:
            # Define custom colors
            field_styles = {
                'asctime': {'color': 'green'},
                'hostname': {'color': 'magenta'},
                'levelname': {'color': 'cyan', 'bold': True},
                'name': {'color': 'blue'},
                'programname': {'color': 'cyan'},
                'username': {'color': 'yellow'}
            }
            
            level_styles = {
                'debug': {'color': 'white'},
                'info': {'color': 'green'},
                'warning': {'color': 'yellow'},
                'error': {'color': 'red'},
                'critical': {'color': 'red', 'bold': True}
            }
            
            coloredlogs.install(
                level='INFO',
                logger=self.logger,
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S',
                field_styles=field_styles,
                level_styles=level_styles
            )
        except Exception as e:
            # If coloredlogs fails, continue without colors
            self.logger.warning(f"Colored logs not available: {e}")
    
    def get_logger(self):
        """লগার ইনস্ট্যান্স রিটার্ন করে"""
        return self.logger
    
    def log_message(self, level: str, message: str, **kwargs):
        """মেসেজ লগ করে"""
        level_methods = {
            'debug': self.logger.debug,
            'info': self.logger.info,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }
        
        if level in level_methods:
            level_methods[level](message, **kwargs)
    
    def log_exception(self, exception: Exception, context: str = ""):
        """এক্সেপশন লগ করে"""
        self.logger.error(
            f"Exception in {context}: {str(exception)}",
            exc_info=True
        )
    
    def log_bot_event(self, event_type: str, user_id: int = None, 
                     chat_id: int = None, details: str = ""):
        """বট ইভেন্ট লগ করে"""
        log_msg = f"[EVENT:{event_type}]"
        
        if user_id:
            log_msg += f" User:{user_id}"
        
        if chat_id:
            log_msg += f" Chat:{chat_id}"
        
        if details:
            log_msg += f" Details:{details}"
        
        self.logger.info(log_msg)
    
    def log_image_generation(self, user_id: int, success: bool, 
                           duration: float = None, error: str = None):
        """ইমেজ জেনারেশন লগ করে"""
        status = "SUCCESS" if success else "FAILED"
        log_msg = f"[IMAGE:{status}] User:{user_id}"
        
        if duration:
            log_msg += f" Time:{duration:.2f}s"
        
        if error:
            log_msg += f" Error:{error}"
        
        if success:
            self.logger.info(log_msg)
        else:
            self.logger.error(log_msg)
    
    def log_safety_check(self, user_id: int, text: str, 
                        is_safe: bool, warnings: list = None):
        """সেফটি চেক লগ করে"""
        status = "SAFE" if is_safe else "UNSAFE"
        
        # Truncate long text
        text_preview = text[:50] + "..." if len(text) > 50 else text
        
        log_msg = f"[SAFETY:{status}] User:{user_id} Text:'{text_preview}'"
        
        if warnings:
            log_msg += f" Warnings:{','.join(warnings)}"
        
        if is_safe:
            self.logger.debug(log_msg)
        else:
            self.logger.warning(log_msg)
    
    def get_log_file_path(self) -> str:
        """বর্তমান লগ ফাইল পাথ রিটার্ন করে"""
        return str(self.today_log_file)
    
    def cleanup_old_logs(self, days: int = 7):
        """পুরানো লগ ফাইল ক্লিনআপ করে"""
        try:
            logs_dir = Path("logs")
            current_time = datetime.now()
            
            for log_file in logs_dir.glob("roastify_*.log"):
                # Get file creation/modification time
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                # Calculate age in days
                age_days = (current_time - file_time).days
                
                if age_days > days:
                    log_file.unlink()
                    self.logger.info(f"Removed old log file: {log_file.name}")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
    
    def log_performance(self, operation: str, duration: float):
        """পারফরম্যান্স লগ করে"""
        if duration > 1.0:  # Log only slow operations
            self.logger.warning(f"[PERF] {operation} took {duration:.2f}s")
        else:
            self.logger.debug(f"[PERF] {operation} took {duration:.2f}s")

# Global logger instance
logger_instance = CustomLogger().get_logger()

# Convenience functions
def get_logger(name=None):
    """লগার ইনস্ট্যান্স পেতে হেল্পার ফাংশন"""
    if name:
        return CustomLogger(name).get_logger()
    return logger_instance

def log_info(message, **kwargs):
    """ইনফো লগ করার জন্য"""
    logger_instance.info(message, **kwargs)

def log_error(message, **kwargs):
    """এরর লগ করার জন্য"""
    logger_instance.error(message, **kwargs)

def log_warning(message, **kwargs):
    """ওয়ার্নিং লগ করার জন্য"""
    logger_instance.warning(message, **kwargs)

def log_debug(message, **kwargs):
    """ডিবাগ লগ করার জন্য"""
    logger_instance.debug(message, **kwargs)

def log_exception(exc, context=""):
    """এক্সেপশন লগ করার জন্য"""
    logger_instance.error(f"Exception in {context}: {exc}", exc_info=True)

# Test the logger
if __name__ == "__main__":
    log_info("লগার টেস্ট শুরু...")
    log_info("বাংলা টেক্সট টেস্ট: রোস্টিফাই বট")
    
    try:
        # Test exception logging
        raise ValueError("টেস্ট এক্সেপশন")
    except Exception as e:
        log_exception(e, "logger_test")
    
    log_info("লগার টেস্ট সম্পন্ন!")
    
    # Show log file location
    print(f"লগ ফাইল: {Path('logs').absolute()}/")
