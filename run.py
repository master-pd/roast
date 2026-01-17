#!/usr/bin/env python3
"""
Simple run script for Roastify Bot
"""

import subprocess
import sys
import os

def check_dependencies():
    """ডিপেন্ডেন্সি চেক করে"""
    print("🔍 Checking dependencies...")
    
    try:
        import telegram
        import PIL
        import sqlalchemy
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstalling dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def check_env_file():
    """এনভায়রনমেন্ট ফাইল চেক করে"""
    print("\n📁 Checking environment configuration...")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("Creating from example...")
        
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as f_example:
                with open(".env", "w") as f_env:
                    f_env.write(f_example.read())
            print("✅ .env file created from .env.example")
            print("⚠️ Please edit .env file with your bot token!")
            return False
        else:
            print("❌ .env.example not found!")
            return False
    else:
        print("✅ .env file found")
        return True

def check_assets():
    """অ্যাসেটস চেক করে"""
    print("\n🎨 Checking assets...")
    
    required_dirs = ["assets/fonts", "assets/backgrounds", "assets/templates"]
    missing_dirs = []
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing asset directories:")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
        
        print("\nWould you like to run the asset setup script? (y/n)")
        choice = input("> ").lower().strip()
        
        if choice == 'y':
            print("\nRunning asset setup...")
            subprocess.call([sys.executable, "setup_assets.py"])
            return True
        else:
            print("⚠️ Running without assets may cause errors!")
            return False
    else:
        print("✅ All asset directories found")
        return True

def main():
    """মেইন ফাংশন"""
    print("🤖 Roastify Bot Runner")
    print("="*50)
    
    # Check everything
    if not check_dependencies():
        return
    
    if not check_env_file():
        print("\n⚠️ Please edit .env file and add your BOT_TOKEN!")
        print("Then run this script again.")
        return
    
    if not check_assets():
        print("\n⚠️ Some assets may be missing, but continuing...")
    
    # Start the bot
    print("\n" + "="*50)
    print("🚀 Starting Roastify Bot...")
    print("="*50)
    print("Press Ctrl+C to stop\n")
    
    try:
        from main import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if BOT_TOKEN is correct in .env")
        print("2. Make sure all dependencies are installed")
        print("3. Check internet connection")
        print("4. Run: python setup_assets.py")

if __name__ == "__main__":
    main()