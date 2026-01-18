#!/usr/bin/env python3
"""
Roastify Bot - Termux Optimized Version
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Fix encoding for Termux
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/roastify_termux.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

class TermuxRoastifyBot:
    """Termux-optimized Roastify Bot"""
    
    def __init__(self):
        from config import Config
        Config.validate()
        
        self.config = Config
        self.roasts = self._load_roasts()
        logger.info("TermuxRoastifyBot initialized")
    
    def _load_roasts(self):
        """রোস্ট লোড করে"""
        return [
            "তোমার আইডিয়াগুলো তো একদম ফার্স্ট ক্লাস! 😂",
            "এই লজিক তো নতুন জেনারেশনের! 🤔",
            "আবার চেষ্টা করো, পারবে! 💪",
            "তুমি লেখো, আমরা মজা করবো! 😄",
            "এই কথার মানে বুঝতে আমার বটেরও সময় লাগবে! ⏰",
            "হুম... ইন্টারেস্টিং! 🤨",
            "রোস্ট প্রস্তুত, কিন্তু আজ ছাড় দিলাম! 😇",
            "তোমার ক্রিয়েটিভিটি দেখে আমি মুগ্ধ! 👏",
            "একটু সোজা করে বলো বুঝি না! 🤷",
            "আমার AI ব্রেন এইটার জন্য প্রস্তুত ছিল না! 🧠"
        ]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """বট শুরু করে"""
        welcome_msg = (
            "🤖 *রোস্টিফাই বট - Termux ভার্সন*\n\n"
            "স্বাগতম! আমি রোস্টিফাই বট।\n"
            "শুধু মেসেজ লিখুন, রোস্ট পাবেন! 😈\n\n"
            "*কমান্ডস:*\n"
            "/start - বট শুরু\n"
            "/help - সাহায্য\n"
            "/roast - র‍্যান্ডম রোস্ট\n"
            "/info - বট ইনফো\n\n"
            f"বট: @{self.config.BOT_USERNAME}"
        )
        await update.message.reply_text(welcome_msg, parse_mode="Markdown")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """সাহায্য দেখায়"""
        help_msg = (
            "📚 *সাহায্য*\n\n"
            "*কীভাবে ব্যবহার করবেন:*\n"
            "1. শুধু কোনো মেসেজ লিখুন\n"
            "2. রিপ্লাই পাবেন রোস্ট সহ\n"
            "3. গ্রুপেও কাজ করে\n\n"
            "*নিয়ম:*\n"
            "• সবাইকে রেসপেক্ট করুন\n"
            "• মজা করুন 🎉\n"
            "• স্প্যাম করবেন না\n\n"
            "সমস্যা হলে: /start আবার চালু করুন"
        )
        await update.message.reply_text(help_msg, parse_mode="Markdown")
    
    async def roast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """র‍্যান্ডম রোস্ট দেয়"""
        import random
        roast = random.choice(self.roasts)
        await update.message.reply_text(roast)
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """বট ইনফো দেখায়"""
        info_msg = (
            "ℹ️ *বট ইনফরমেশন*\n\n"
            f"• নাম: {self.config.BOT_USERNAME}\n"
            f"• ভার্সন: Termux 1.0\n"
            f"• Python: {sys.version.split()[0]}\n"
            f"• OS: Android/Termux\n"
            f"• স্ট্যাটাস: সক্রিয় ✅\n\n"
            "রোস্টের জন্য প্রস্তুত! 😈"
        )
        await update.message.reply_text(info_msg, parse_mode="Markdown")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """টেক্সট মেসেজ হ্যান্ডল করে"""
        user_text = update.message.text
        
        if not user_text or len(user_text.strip()) < 2:
            await update.message.reply_text("একটু লম্বা মেসেজ লিখুন! ✍️")
            return
        
        import random
        import time
        
        # Show typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Small delay for realism
        await asyncio.sleep(0.5)
        
        # Select roast based on text length
        if len(user_text) > 50:
            roast = "বাহ! এত লম্বা মেসেজ! সংক্ষিপ্ত করলে ভালো হতো! 📝"
        elif len(user_text) < 10:
            roast = "সংক্ষিপ্ত ও সুন্দর! কিন্তু একটু বিস্তারিত বললে ভালো হতো! 🤔"
        else:
            roast = random.choice(self.roasts)
        
        # Add user name if available
        user = update.effective_user
        if user and user.first_name:
            roast = f"{user.first_name}, {roast}"
        
        await update.message.reply_text(roast)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """এরর হ্যান্ডল করে"""
        logger.error(f"Error: {context.error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "😓 সাময়িক সমস্যা! আবার চেষ্টা করুন।"
                )
            except:
                pass
    
    def run(self):
        """বট চালু করে"""
        try:
            print("\n" + "="*50)
            print("🤖 Roastify Bot - Termux Edition")
            print("="*50)
            print(f"Token: {self.config.BOT_TOKEN[:10]}...")
            print(f"Bot: @{self.config.BOT_USERNAME}")
            print("="*50 + "\n")
            
            # Create application
            app = ApplicationBuilder().token(self.config.BOT_TOKEN).build()
            
            # Add handlers
            app.add_handler(CommandHandler("start", self.start))
            app.add_handler(CommandHandler("help", self.help))
            app.add_handler(CommandHandler("roast", self.roast))
            app.add_handler(CommandHandler("info", self.info))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
            
            # Add error handler
            app.add_error_handler(self.error_handler)
            
            # Set bot commands
            async def set_commands():
                commands = [
                    BotCommand("start", "বট শুরু"),
                    BotCommand("help", "সাহায্য"),
                    BotCommand("roast", "রোস্ট পান"),
                    BotCommand("info", "বট ইনফো"),
                ]
                await app.bot.set_my_commands(commands)
            
            # Run
            print("🚀 Starting bot... (Press Ctrl+C to stop)")
            app.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
        except Exception as e:
            logger.error(f"Failed to start: {e}")
            print(f"\n❌ Error: {e}")
            print("\nCheck if:")
            print("1. BOT_TOKEN is correct in .env")
            print("2. Internet connection is working")
            print("3. Termux has proper permissions")

def main():
    """মেইন ফাংশন"""
    bot = TermuxRoastifyBot()
    bot.run()

if __name__ == "__main__":
    main()
