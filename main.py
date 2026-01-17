#!/usr/bin/env python3
"""
Roastify Telegram Bot - Main Entry Point
তুমি লেখো, বাকি অপমান আমরা করবো 😈
"""

import os
import sys
import signal
import asyncio
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from utils.logger import logger
from bot import RoastifyBot

class BotRunner:
    """বট রানার ক্লাস - প্রপার শাটডাউন হ্যান্ডলিং সহ"""
    
    def __init__(self):
        self.bot = None
        self._setup_signal_handlers()
        self._check_python_version()
    
    def _check_python_version(self):
        """Python ভার্সন চেক করে"""
        import platform
        python_version = platform.python_version()
        logger.info(f"Python version: {python_version}")
        
        # Check minimum version
        version_tuple = tuple(map(int, python_version.split('.')))
        if version_tuple < (3, 8):
            logger.warning(f"Python 3.8+ recommended. Current: {python_version}")
    
    def _setup_signal_handlers(self):
        """সিগনাল হ্যান্ডলার সেটআপ করে"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        logger.info("Signal handlers set up")
    
    def _signal_handler(self, signum, frame):
        """সিগনাল হ্যান্ডল করে"""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        logger.info(f"Received {signal_name}, shutting down gracefully...")
        self.shutdown()
    
    def _check_environment(self):
        """এনভায়রনমেন্ট চেক করে"""
        print("🔍 Checking environment...")
        
        # Check .env file
        env_file = current_dir / ".env"
        if not env_file.exists():
            print("❌ .env file not found!")
            print("Please create .env file from .env.example")
            print("Example: cp .env.example .env")
            print("Then edit .env with your BOT_TOKEN")
            return False
        
        # Check BOT_TOKEN in environment
        from dotenv import load_dotenv
        load_dotenv()
        
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token or bot_token == "your_bot_token_here":
            print("❌ BOT_TOKEN not set or is default!")
            print("Please edit .env file and add your bot token")
            return False
        
        print("✅ Environment check passed")
        return True
    
    def _check_dependencies(self):
        """ডিপেন্ডেন্সি চেক করে"""
        print("📦 Checking dependencies...")
        
        required_packages = [
            "python-telegram-bot",
            "pillow",
            "python-dotenv",
            "sqlalchemy",
            "apscheduler",
            "emoji",
            "pytz",
            "requests"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("\nInstalling dependencies...")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("✅ Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install dependencies")
                return False
        else:
            print("✅ All dependencies installed")
            return True
    
    def _setup_directories(self):
        """প্রয়োজনীয় ডিরেক্টরি তৈরি করে"""
        print("📁 Setting up directories...")
        
        directories = [
            current_dir / "logs",
            current_dir / "generated",
            current_dir / "temp",
            current_dir / "assets",
            current_dir / "assets/fonts",
            current_dir / "assets/backgrounds",
            current_dir / "assets/templates",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {directory.relative_to(current_dir)}")
        
        print("✅ Directories set up")
        
        # Check for default assets
        default_font = current_dir / "assets/fonts/arial.ttf"
        if not default_font.exists():
            print("⚠️ Warning: Default font not found in assets/fonts/")
            print("   You may need to add font files manually")
        
        return True
    
    def _run_setup_script(self):
        """সেটআপ স্ক্রিপ্ট রান করে"""
        setup_script = current_dir / "setup_assets.py"
        
        if setup_script.exists():
            print("🛠️ Running asset setup script...")
            try:
                import subprocess
                result = subprocess.run([sys.executable, str(setup_script)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Asset setup completed")
                    return True
                else:
                    print(f"❌ Asset setup failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Error running setup script: {e}")
                return False
        else:
            print("⚠️ Setup script not found, skipping...")
            return True
    
    def _print_banner(self):
        """বট ব্যানার প্রিন্ট করে"""
        banner = """
╔══════════════════════════════════════════════════════════╗
║                 🤖  ROASTIFY BOT  🤖                    ║
║        তুমি লেখো, বাকি অপমান আমরা করবো 😈           ║
╚══════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def _print_system_info(self):
        """সিস্টেম ইনফো প্রিন্ট করে"""
        import platform
        import psutil
        
        print("📊 System Information:")
        print(f"  • OS: {platform.system()} {platform.release()}")
        print(f"  • Python: {platform.python_version()}")
        print(f"  • CPU: {psutil.cpu_count()} cores")
        print(f"  • RAM: {psutil.virtual_memory().total // (1024**3)} GB")
        print(f"  • Disk: {psutil.disk_usage('/').free // (1024**3)} GB free")
    
    def startup(self):
        """বট শুরু করে"""
        try:
            self._print_banner()
            
            # System info
            self._print_system_info()
            print("=" * 60)
            
            # Run checks
            if not self._check_environment():
                sys.exit(1)
            
            if not self._check_dependencies():
                sys.exit(1)
            
            if not self._setup_directories():
                sys.exit(1)
            
            if not self._run_setup_script():
                print("⚠️ Continuing without asset setup...")
            
            print("\n" + "=" * 60)
            print("🚀 Initializing Roastify Bot...")
            print("=" * 60)
            
            # Create and start bot
            self.bot = RoastifyBot()
            
            # Run the bot
            logger.info("=" * 50)
            logger.info("Starting Roastify Bot")
            logger.info("=" * 50)
            
            self.bot.run()
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user (Ctrl+C)")
            self.shutdown()
        except Exception as e:
            logger.error(f"Failed to start bot: {e}", exc_info=True)
            print(f"\n❌ Fatal error: {e}")
            print("\nTroubleshooting steps:")
            print("1. Check if BOT_TOKEN is correct in .env")
            print("2. Run: pip install -r requirements.txt")
            print("3. Check internet connection")
            print("4. Run: python setup_assets.py")
            self.shutdown()
    
    def shutdown(self):
        """বট বন্ধ করে"""
        print("\n\n🛑 Shutting down bot...")
        
        if self.bot and self.bot.application:
            try:
                # Try to stop the application
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule shutdown
                    asyncio.create_task(self.bot.application.shutdown())
                    asyncio.create_task(self.bot.application.stop())
            except:
                pass
        
        logger.info("Bot shutdown complete")
        
        # Print shutdown message
        print("👋 Bot stopped successfully")
        print("\nThank you for using Roastify Bot!")
        print("For support, check the logs in logs/ directory")
        
        sys.exit(0)

def main():
    """মেইন ফাংশন"""
    runner = BotRunner()
    runner.startup()

if __name__ == "__main__":
    main()
