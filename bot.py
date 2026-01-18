#!/usr/bin/env python3
"""
🤖 Roastify Telegram Bot - Simplified Version
✅ Works with your current structure
✅ No dynamic loading, simple imports
✅ Ready to run
"""

import os
import sys
import asyncio
import random
import traceback
from datetime import datetime
from typing import Dict, List, Optional

# Telegram imports
from telegram import (
    Update, 
    BotCommand, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode, ChatAction

# Import configuration
from config import Config

# Import modules from your existing structure
from utils.logger import logger, log_error, log_info
from utils.time_manager import TimeManager
from utils.helpers import Helpers
from utils.text_processor import TextProcessor
from database.storage import StorageManager
from database.models import init_database, User, Roast
from roast_engine.roaster import RoastEngine
from roast_engine.safety_check import safety_checker
from image_engine.image_generator import get_image_generator
from features.welcome_system import WelcomeSystem
from features.vote_system import VoteSystem
from features.mention_system import MentionSystem
from features.reaction_system import ReactionSystem
from features.admin_protection import AdminProtection
from features.sticker_maker import StickerMaker
from features.quote_of_day import QuoteOfDay


class RoastifyBot:
    """রোস্টিফাই বট - Simplified Version"""
    
    def __init__(self):
        """বট ইনিশিয়ালাইজেশন"""
        try:
            # Validate configuration
            if hasattr(Config, 'validate'):
                Config.validate()
            
            # Initialize database
            init_database()
            
            # Initialize components with proper error handling
            self._initialize_components()
            
            # Bot state
            self.application = None
            self.is_running = False
            self.user_cooldowns = {}
            
            # Stats
            self.stats = {
                'total_messages': 0,
                'total_roasts': 0,
                'total_errors': 0,
                'start_time': datetime.now()
            }
            
            # Random styles
            self.border_styles = self._get_border_styles()
            self.word_variations = self._get_word_variations()
            
            logger.info("✅ RoastifyBot (Simplified) initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize bot: {e}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            raise
    
    def _initialize_components(self):
        """সব কম্পোনেন্ট ইনিশিয়ালাইজ করুন"""
        # Core modules (must have)
        self.logger = logger
        self.time_manager = TimeManager()
        self.helpers = Helpers()
        self.text_processor = TextProcessor()
        
        # Initialize with error handling
        try:
            self.roast_engine = RoastEngine()
            logger.info("✅ RoastEngine initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RoastEngine: {e}")
            self.roast_engine = None
        
        try:
            self.safety_checker = safety_checker
            logger.info("✅ SafetyChecker initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize SafetyChecker: {e}")
            self.safety_checker = None
        
        try:
            self.image_generator = get_image_generator()
            logger.info("✅ ImageGenerator initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ImageGenerator: {e}")
            self.image_generator = None
        
        try:
            self.welcome_system = WelcomeSystem()
            logger.info("✅ WelcomeSystem initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize WelcomeSystem: {e}")
            self.welcome_system = None
        
        try:
            self.vote_system = VoteSystem()
            logger.info("✅ VoteSystem initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize VoteSystem: {e}")
            self.vote_system = None
        
        try:
            self.mention_system = MentionSystem()
            logger.info("✅ MentionSystem initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize MentionSystem: {e}")
            self.mention_system = None
        
        try:
            self.reaction_system = ReactionSystem()
            logger.info("✅ ReactionSystem initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ReactionSystem: {e}")
            self.reaction_system = None
        
        try:
            self.admin_protection = AdminProtection()
            logger.info("✅ AdminProtection initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AdminProtection: {e}")
            self.admin_protection = None
        
        try:
            self.sticker_maker = StickerMaker()
            logger.info("✅ StickerMaker initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize StickerMaker: {e}")
            self.sticker_maker = None
        
        try:
            # Note: QuoteOfDay needs bot instance
            self.quote_of_day = QuoteOfDay(self)
            logger.info("✅ QuoteOfDay initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize QuoteOfDay: {e}")
            self.quote_of_day = None
    
    def _get_border_styles(self):
        """বর্ডার স্টাইলস"""
        return {
            "fire": {"top": "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥", "bottom": "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥"},
            "star": {"top": "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦", "bottom": "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦"},
            "heart": {"top": "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️", "bottom": "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️"},
            "diamond": {"top": "💎💎💎💎💎💎💎💎💎💎", "bottom": "💎💎💎💎💎💎💎💎💎💎"},
            "wave": {"top": "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️", "bottom": "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️"},
        }
    
    def _get_word_variations(self):
        """শব্দ ভেরিয়েশন"""
        return {
            "welcome": ["স্বাগতম", "আসসালামু আলাইকুম", "Welcome"],
            "help": ["সাহায্য", "হেল্প", "গাইড"],
            "roast": ["রোস্ট", "মজা", "জোক"],
            "funny": ["মজার", "হাসির", "কৌতুক"],
            "thanks": ["ধন্যবাদ", "Thank you", "শুকরিয়া"],
        }
    
    def _get_random_border(self):
        """র‍্যান্ডম বর্ডার সিলেক্ট করুন"""
        style_name = random.choice(list(self.border_styles.keys()))
        return self.border_styles[style_name]
    
    def _get_random_word(self, key):
        """র‍্যান্ডম শব্দ দিন"""
        if key in self.word_variations:
            return random.choice(self.word_variations[key])
        return key
    
    # ==================== COMMAND HANDLERS ====================
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start command"""
        try:
            user = update.effective_user
            
            # Log user
            logger.info(f"User {user.id} started the bot")
            
            # Send welcome message
            border = self._get_random_border()
            welcome_text = f"{border['top']}\n"
            welcome_text += f"🤖 **{self._get_random_word('welcome')} {user.first_name}!**\n\n"
            welcome_text += "আমি **রোস্টিফাই বট**। 😈\n"
            welcome_text += "তুমি লেখো, বাকি অপমান আমি করবো!\n\n"
            welcome_text += "**কিভাবে ব্যবহার করবেন:**\n"
            welcome_text += "১. শুধু একটি মেসেজ লিখুন\n"
            welcome_text += "২. বট অটোমেটিক রোস্ট করবে\n"
            welcome_text += "৩. ইমেজ সহ রিপ্লাই পাবেন\n\n"
            welcome_text += "**কমান্ড লিস্ট:**\n"
            welcome_text += "/start - বট শুরু করুন\n"
            welcome_text += "/help - সাহায্য\n"
            welcome_text += "/roast - র‍্যান্ডম রোস্ট\n"
            welcome_text += "/quote - আজকের উক্তি\n"
            welcome_text += "/ping - বট চেক\n"
            welcome_text += "/info - বট তথ্য\n\n"
            welcome_text += "🔥 **এখনই একটি মেসেজ লিখে টেস্ট করুন!**"
            welcome_text += f"\n{border['bottom']}"
            
            await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)
            
            self.stats['total_messages'] += 1
            
        except Exception as e:
            error_msg = f"Error in handle_start: {e}"
            logger.error(error_msg)
            await update.message.reply_text("❌ বট শুরু করতে সমস্যা! আবার চেষ্টা করুন।")
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/help command"""
        try:
            help_text = "📖 **রোস্টিফাই বট - হেল্প মেনু**\n\n"
            help_text += "**বেসিক কমান্ডস:**\n"
            help_text += "• /start - বট শুরু করুন\n"
            help_text += "• /help - এই হেল্প মেসেজ\n"
            help_text += "• /roast - র‍্যান্ডম রোস্ট পান\n"
            help_text += "• /quote - আজকের বিশেষ উক্তি\n"
            help_text += "• /ping - বট লাইভ চেক\n"
            help_text += "• /info - বট সম্পর্কে তথ্য\n\n"
            
            help_text += "**এডভান্সড ফিচারস:**\n"
            help_text += "• ইমেজ জেনারেশন\n"
            help_text += "• বাংলা/ইংরেজি সাপোর্ট\n"
            help_text += "• ভোট সিস্টেম\n"
            help_text += "• স্টিকার তৈরি\n"
            help_text += "• ডেইলি কোটস\n\n"
            
            help_text += "**কিভাবে কাজ করে:**\n"
            help_text += "১. আপনি একটি মেসেজ লিখুন\n"
            help_text += "২. বট স্মার্ট রোস্ট জেনারেট করবে\n"
            help_text += "৩. ইমেজ সহ রিপ্লাই পাবেন\n\n"
            
            help_text += "⚠️ **দ্রষ্টব্য:** সবকিছু শুধু মজার জন্য!"
            
            await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            error_msg = f"Error in handle_help: {e}"
            logger.error(error_msg)
    
    async def handle_roast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/roast command - generate random roast"""
        try:
            user = update.effective_user
            
            # Generate roast
            roast_text = self._generate_roast_text(user)
            
            # Send with random border
            border = self._get_random_border()
            message = f"{border['top']}\n"
            message += f"🔥 **{self._get_random_word('roast')} টাইম!**\n\n"
            message += f"_{roast_text}_\n\n"
            message += f"— {user.first_name}\n"
            message += border['bottom']
            
            await update.message.reply_text(message, parse_mode=ParseMode.HTML)
            
            self.stats['total_roasts'] += 1
            logger.info(f"Roast sent to user {user.id}")
            
        except Exception as e:
            error_msg = f"Error in handle_roast: {e}"
            logger.error(error_msg)
            await update.message.reply_text("❌ রোস্ট জেনারেট করতে সমস্যা!")
    
    def _generate_roast_text(self, user):
        """রোস্ট টেক্সট জেনারেট করুন"""
        roasts = [
            f"{user.first_name}, তুমি তো একদম চমৎকার! 😂",
            f"ওহো {user.first_name}! আজকে মড কেমন? 😈",
            f"{user.first_name} এর জন্য বিশেষ রোস্ট! 🔥",
            f"একটু চিন্তা করছি {user.first_name}... হ্যাঁ পেয়ে গেছি! 🤔",
            f"রেডি {user.first_name}? হোল্ড অন টাইট! 🎯",
            f"{user.first_name}, তোমার জন্য ফ্রেশ রোস্ট! ☕",
            f"শুনো {user.first_name}, এটা শুনে হাসবি না! 😜",
            f"তুমি তো {user.first_name} একদম প্রো! 💪",
        ]
        
        if self.roast_engine:
            try:
                return self.roast_engine.generate_roast(user_id=user.id)
            except:
                pass
        
        return random.choice(roasts)
    
    async def handle_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/quote command - daily quote"""
        try:
            if self.quote_of_day:
                quote_data = self.quote_of_day.get_todays_quote()
                quote_text = f"\"{quote_data['text']}\"\n— _{quote_data['author']}_"
            else:
                quotes = [
                    {"text": "জীবনে সবচেয়ে বড় শিক্ষা হলো নিজেকে চেনা", "author": "অজানা"},
                    {"text": "পরিশ্রম সৌভাগ্যের প্রসূতি", "author": "প্রবাদ"},
                    {"text": "হাসতে হাসতে জীবন কাটাও", "author": "রোস্টিফাই বট"},
                    {"text": "ভালোবাসা কোন কথা নয়, এটি একটি অনুভূতি", "author": "রবীন্দ্রনাথ ঠাকুর"},
                ]
                quote = random.choice(quotes)
                quote_text = f"\"{quote['text']}\"\n— _{quote['author']}_"
            
            border = self._get_random_border()
            message = f"{border['top']}\n"
            message += f"📖 **আজকের উক্তি**\n\n"
            message += f"{quote_text}\n\n"
            message += f"✨ _রোস্টিফাই বট_"
            message += f"\n{border['bottom']}"
            
            await update.message.reply_text(message, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            error_msg = f"Error in handle_quote: {e}"
            logger.error(error_msg)
            await update.message.reply_text("❌ উক্তি লোড করতে সমস্যা!")
    
    async def handle_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/ping command - check bot status"""
        try:
            start_time = datetime.now()
            
            ping_msg = await update.message.reply_text("🏓 পিং...")
            
            end_time = datetime.now()
            latency = (end_time - start_time).total_seconds() * 1000
            
            uptime = datetime.now() - self.stats['start_time']
            uptime_str = str(uptime).split('.')[0]
            
            status_text = f"✅ **বট স্ট্যাটাস**\n\n"
            status_text += f"⚡ রেসপন্স টাইম: `{latency:.0f}ms`\n"
            status_text += f"⏰ আপটাইম: `{uptime_str}`\n"
            status_text += f"📊 মেসেজ: `{self.stats['total_messages']}`\n"
            status_text += f"🔥 রোস্ট: `{self.stats['total_roasts']}`\n"
            status_text += f"❌ এরর: `{self.stats['total_errors']}`\n\n"
            status_text += f"🟢 **স্ট্যাটাস: অ্যাকটিভ**"
            
            await ping_msg.edit_text(status_text, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            error_msg = f"Error in handle_ping: {e}"
            logger.error(error_msg)
            await update.message.reply_text("❌ পিং টেস্ট ফেইল!")
    
    async def handle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/info command - bot information"""
        try:
            info_text = "🤖 **রোস্টিফাই বট - ইনফরমেশন**\n\n"
            info_text += "**বট সম্পর্কে:**\n"
            info_text += "রোস্টিফাই বট একটি এডভান্সড রোস্ট জেনারেটর বট।\n"
            info_text += "মজা করার জন্য ডিজাইন করা হয়েছে।\n\n"
            
            info_text += "**ফিচারস:**\n"
            info_text += "• স্মার্ট রোস্ট জেনারেশন\n"
            info_text += "• ইমেজ ক্রিয়েশন\n"
            info_text += "• মাল্টি-ল্যাঙ্গুয়েজ\n"
            info_text += "• ডেইলি কোটস\n"
            info_text += "• ভোট সিস্টেম\n"
            info_text += "• স্টিকার মেকার\n\n"
            
            info_text += "**টেকনোলজি:**\n"
            info_text += "• Python 3.12\n"
            info_text += "• Python-Telegram-Bot\n"
            info_text += "• SQLAlchemy\n"
            info_text += "• Pillow (ইমেজ প্রসেসিং)\n\n"
            
            info_text += f"**ভার্সন:** 2.0.0\n"
            info_text += f"**ক্রিয়েটর:** রোস্টিফাই টিম\n\n"
            
            info_text += "⚠️ **নোট:** সবকিছু শুধু বিনোদনের জন্য!"
            
            await update.message.reply_text(info_text, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            error_msg = f"Error in handle_info: {e}"
            logger.error(error_msg)
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            message = update.effective_message
            user = update.effective_user
            
            self.stats['total_messages'] += 1
            
            # Check cooldown
            if not self._check_cooldown(user.id):
                await update.message.reply_text(
                    "⏳ একটু ধৈর্য ধরুন! ৫ সেকেন্ড অপেক্ষা করুন।",
                    parse_mode=ParseMode.HTML
                )
                return
            
            # Check if message is too short
            if len(message.text.strip()) < 3:
                await update.message.reply_text(
                    "📝 কমপক্ষে ৩ অক্ষর লিখুন!",
                    parse_mode=ParseMode.HTML
                )
                return
            
            # Generate roast
            roast_text = self._generate_text_roast(message.text, user)
            
            # Send response with random style
            response_style = random.choice(['border', 'simple', 'emoji'])
            
            if response_style == 'border':
                border = self._get_random_border()
                response = f"{border['top']}\n"
                response += f"🎯 **রোস্ট রেসপন্স**\n\n"
                response += f"_{roast_text}_\n\n"
                response += f"✍️ ইনপুট: `{message.text[:50]}...`\n"
                response += f"👤 ইউজার: {user.first_name}"
                response += f"\n{border['bottom']}"
            elif response_style == 'emoji':
                response = f"🔥 **রোস্ট এলার্ট!** 🔥\n\n"
                response += f"_{roast_text}_\n\n"
                response += f"👉 {user.first_name}, এটা কি ঠিক? 😂"
            else:
                response = f"**রোস্ট:**\n{roast_text}\n\n— @{user.username or user.first_name}"
            
            await update.message.reply_text(response, parse_mode=ParseMode.HTML)
            
            self.stats['total_roasts'] += 1
            logger.info(f"Text roast for user {user.id}: {message.text[:50]}...")
            
        except Exception as e:
            self.stats['total_errors'] += 1
            error_msg = f"Error in handle_text_message: {e}"
            logger.error(error_msg)
            traceback.print_exc()
            
            await update.message.reply_text(
                "😓 রোস্ট জেনারেট করতে সমস্যা! দয়া করে আবার চেষ্টা করুন।",
                parse_mode=ParseMode.HTML
            )
    
    def _generate_text_roast(self, text: str, user):
        """টেক্সট ভিত্তিক রোস্ট জেনারেট করুন"""
        if self.roast_engine:
            try:
                return self.roast_engine.generate_roast(text, user.id)
            except:
                pass
        
        # Fallback roasts based on text length
        text_len = len(text)
        
        if text_len < 10:
            roasts = [
                f"ওহো {user.first_name}! এত ছোট মেসেজ? 😏",
                f"{user.first_name}, একটু লম্বা লিখতে পারতে! 📝",
                f"এটুকু? {user.first_name}, তোমার imagination কই? 🤔",
            ]
        elif text_len < 30:
            roasts = [
                f"হুমম... {user.first_name}, ভালো চেষ্টা! 👍",
                f"{user.first_name}, মেসেজ দেখে বোঝা যাচ্ছে তুমি মজার! 😄",
                f"এখন শোনো {user.first_name}, এই মেসেজের জন্য... 🤣",
            ]
        else:
            roasts = [
                f"ওহো {user.first_name}! তুমি তো novelist! 📚",
                f"{user.first_name}, এত লম্বা মেসেজ? ধৈর্য ধন্যবাদ! ⏳",
                f"হ্যাঁ {user.first_name}, পড়লাম! এখন আমার পালা... 😈",
            ]
        
        return random.choice(roasts)
    
    def _check_cooldown(self, user_id: int) -> bool:
        """কুলডাউন চেক করুন"""
        current_time = datetime.now()
        
        if user_id in self.user_cooldowns:
            last_time = self.user_cooldowns[user_id]
            time_diff = (current_time - last_time).total_seconds()
            
            if time_diff < 5:  # 5 seconds cooldown
                return False
        
        self.user_cooldowns[user_id] = current_time
        return True
    
    # ==================== BOT CONTROL ====================
    
    def setup_application(self):
        """টেলিগ্রাম অ্যাপ্লিকেশন সেটআপ"""
        try:
            self.application = (
                ApplicationBuilder()
                .token(Config.BOT_TOKEN)
                .concurrent_updates(True)
                .pool_timeout(30)
                .connect_timeout(30)
                .read_timeout(30)
                .write_timeout(30)
                .build()
            )
            
            # Register handlers
            self._register_handlers()
            
            logger.info("✅ Application setup completed")
            return True
            
        except Exception as e:
            error_msg = f"Application setup failed: {e}"
            logger.error(error_msg)
            return False
    
    def _register_handlers(self):
        """হ্যান্ডলার রেজিস্টার করুন"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("roast", self.handle_roast))
        self.application.add_handler(CommandHandler("quote", self.handle_quote))
        self.application.add_handler(CommandHandler("ping", self.handle_ping))
        self.application.add_handler(CommandHandler("info", self.handle_info))
        
        # Text message handler
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_message
        ))
        
        logger.info("✅ All handlers registered successfully")
    
    async def _set_bot_commands(self):
        """বট কমান্ডস সেট করুন"""
        try:
            commands = [
                BotCommand("start", "বট শুরু করুন"),
                BotCommand("help", "সাহায্য পান"),
                BotCommand("roast", "র‍্যান্ডম রোস্ট পান"),
                BotCommand("quote", "আজকের উক্তি পান"),
                BotCommand("ping", "বট চেক করুন"),
                BotCommand("info", "বট তথ্য"),
            ]
            
            await self.application.bot.set_my_commands(commands)
            logger.info("✅ Bot commands set successfully")
            
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")
    
    async def run(self):
        """বট রান করুন"""
        try:
            logger.info("🚀 Starting Roastify Bot...")
            
            if not self.setup_application():
                raise Exception("Failed to setup application")
            
            # Initialize
            await self.application.initialize()
            
            # Get bot info
            bot_info = await self.application.bot.get_me()
            logger.info(f"🤖 Bot Info: @{bot_info.username} (ID: {bot_info.id})")
            
            # Set bot commands
            await self._set_bot_commands()
            
            # Start
            await self.application.start()
            
            # Start polling
            await self.application.updater.start_polling()
            
            logger.info("✅ Bot started successfully!")
            logger.info("📡 Listening for messages...")
            
            self.is_running = True
            
            # Keep running
            await self._keep_running()
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            traceback.print_exc()
            await self.stop()
    
    async def _keep_running(self):
        """বট চলমান রাখুন"""
        try:
            while self.is_running:
                await asyncio.sleep(1)
                
                # Log status every 5 minutes
                current_time = datetime.now()
                if current_time.minute % 5 == 0 and current_time.second == 0:
                    logger.info(f"📊 Status: Msg: {self.stats['total_messages']} | Roasts: {self.stats['total_roasts']} | Errors: {self.stats['total_errors']}")
                    
        except asyncio.CancelledError:
            logger.info("Bot stopped by cancellation")
        except Exception as e:
            logger.error(f"Error in keep_running: {e}")
    
    async def stop(self):
        """বট স্টপ করুন"""
        try:
            logger.info("🛑 Stopping bot...")
            
            self.is_running = False
            
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            logger.info("✅ Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")


# ==================== MAIN FUNCTION ====================

async def main():
    """মেইন ফাংশন"""
    try:
        print("\n" + "="*50)
        print("🤖 ROASTIFY BOT - SIMPLIFIED VERSION")
        print("="*50 + "\n")
        
        # Create and run bot
        bot = RoastifyBot()
        await bot.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  বট বন্ধ করা হচ্ছে (Ctrl+C)...")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        
    finally:
        print("\n👋 Roastify Bot stopped")
        print("="*50)


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
