import logging
import coloredlogs
from datetime import datetime
import os

class Logger:
    def __init__(self, name="RoastifyBot"):
        self.logger = logging.getLogger(name)
        
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG)
            
            # Create logs directory if not exists
            if not os.path.exists("logs"):
                os.makedirs("logs")
            
            # File handler
            file_handler = logging.FileHandler(
                f"logs/roastify_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            coloredlogs.install(
                level='INFO',
                logger=self.logger,
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger

# Global logger instance
logger = Logger().get_logger()