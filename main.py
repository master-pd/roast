#!/usr/bin/env python3
"""
Roastify Telegram Bot - Main Entry Point
তুমি লেখো, বাকি অপমান আমরা করবো 😈
"""

import os
import sys
import signal
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import logger
from bot import RoastifyBot

class BotRunner:
    def __init__(self):
        self.bot = None
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """সিগনাল হ্যান্ডলার সেটআপ করে"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        logger.info("Signal handlers set up")
    
    def _signal_handler(self, signum, frame):
        """সিগনাল হ্যান্ডল করে"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
    
    def startup(self):
        """বট শুরু করে"""
        try:
            logger.info("=" * 50)
            logger.info("🚀 Starting Roastify Bot")
            logger.info("=" * 50)
            
            # Check environment
            self._check_environment()
            
            # Create and start bot
            self.bot = RoastifyBot()
            
            # Import asyncio here to avoid event loop issues
            import asyncio
            
            # Run bot
            asyncio.run(self.bot.start())
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            self.shutdown()
    
    def _check_environment(self):
        """এনভায়রনমেন্ট চেক করে"""
        required_vars = ["BOT_TOKEN", "OWNER_ID"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.error("Please set these variables in .env file or environment")
            sys.exit(1)
        
        # Check assets directory
        assets_path = Path("assets")
        if not assets_path.exists():
            logger.warning("Assets directory not found, creating...")
            assets_path.mkdir(parents=True, exist_ok=True)
            (assets_path / "fonts").mkdir(exist_ok=True)
            (assets_path / "backgrounds").mkdir(exist_ok=True)
            (assets_path / "templates").mkdir(exist_ok=True)
        
        logger.info("Environment check passed")
    
    def shutdown(self):
        """বট বন্ধ করে"""
        logger.info("Shutting down bot...")
        
        if self.bot:
            import asyncio
            try:
                asyncio.run(self.bot.stop())
            except:
                pass
        
        logger.info("Bot shutdown complete")
        sys.exit(0)

def main():
    """মেইন ফাংশন"""
    runner = BotRunner()
    runner.startup()

if __name__ == "__main__":
    main()