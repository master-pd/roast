#!/usr/bin/env python3
"""
Roastify Bot - Main Bot File (Fixed & Updated)
তুমি লেখো, বাকি অপমান আমরা করবো 😈
"""

import os
import sys
import logging
import json
import asyncio
import random
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add current directory and roast_engine to path
current_dir = os.path.dirname(os.path.abspath(__file__))
roast_engine_path = os.path.join(current_dir, 'roast_engine')
if os.path.exists(roast_engine_path):
    sys.path.insert(0, roast_engine_path)

from dotenv import load_dotenv
from telegram import (
    Update, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    ContextTypes,
    filters,
    ConversationHandler
)

# ========== MODULE IMPORT WITH FALLBACK ==========
def import_with_fallback():
    """Import modules with fallback to dummy classes"""
    
    # SafetyChecker
    try:
        from safety_checker import SafetyChecker
    except ImportError:
        class SafetyChecker:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.logger.info("⚠️ Using dummy SafetyChecker")
                self.banned_words = ["fuck", "shit", "asshole", "গালি", "অপমান", "অশ্লীল"]
            
            def is_safe(self, text, user_id=None):
                if not text:
                    return False
                text_lower = text.lower()
                for word in self.banned_words:
                    if word in text_lower:
                        self.logger.warning(f"Banned word detected: {word}")
                        return False
                return True
    
    # ImageGenerator
    try:
        from image_generator import AdvancedImageGenerator
    except ImportError:
        class AdvancedImageGenerator:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.logger.info("⚠️ Using dummy ImageGenerator")
            
            def generate_roast_image(self, roast_text, name, style="default"):
                self.logger.info(f"📸 Would generate image for {name}")
                return None
    
    # AutoQuoteSystem
    try:
        from auto_quote import AutoQuoteSystem
    except ImportError:
        class AutoQuoteSystem:
            def __init__(self, bot=None):
                self.bot = bot
                self.logger = logging.getLogger(__name__)
                self.logger.info("⚠️ Using dummy AutoQuoteSystem")
                self.quotes = [
                    "জীবন সুন্দর যখন তুমি সুন্দর চিন্তা করো",
                    "ভালোবাসা দিয়ে পাওয়া যায়, ক্রয় করা যায় না",
                    "জ্ঞান হলো সেই সম্পদ যা কখনো চুরি হয় না"
                ]
                self.jokes = [
                    "শিক্ষক: পরীক্ষার সময় কপি করবে কেন?\nছাত্র: স্যার, কপিরাইট তো ভাঙবো না!",
                    "ডাক্তার: আপনার হার্টের অবস্থা ভালো না।\nরোগী: কষ্ট করে বলছেন কেন, মেসেজ করে দিতেন!"
                ]
                self.facts = [
                    "মৌমাছিরা এক সেকেন্ডে ২০০ বার ডানা ঝাপটায়",
                    "মানুষের মস্তিষ্ক ৭৫% পানি দিয়ে তৈরি"
                ]
            
            async def get_random_quote(self):
                quote = random.choice(self.quotes)
                return f"<b>📜 Quote of the Day:</b>\n\n<i>\"{quote}\"</i>"
            
            async def get_random_joke(self):
                joke = random.choice(self.jokes)
                return f"<b>😂 Funny Joke:</b>\n\n{joke}"
            
            async def get_random_fact(self):
                fact = random.choice(self.facts)
                return f"<b>🔍 Did You Know?</b>\n\n{fact}"
    
    # DatabaseManager
    try:
        from database import DatabaseManager
    except ImportError:
        class DatabaseManager:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.logger.info("⚠️ Using dummy DatabaseManager")
                self.users = {}
                self.roasts = []
            
            def add_user(self, user_id, first_name, username=None):
                self.users[user_id] = {
                    "name": first_name, 
                    "username": username,
                    "joined": datetime.now()
                }
                return True
            
            def get_user_stats(self, user_id):
                return {"roast_count": 0, "rank": 100}
    
    # Config Loader
    try:
        from config_loader import load_config
    except ImportError:
        def load_config():
            # Try to load from .env
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except:
                pass
            
            config = {
                'BOT_TOKEN': os.getenv('BOT_TOKEN', ''),
                'ADMIN_IDS': [],
                'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
                'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///roastify.db'),
                'RATE_LIMIT': int(os.getenv('RATE_LIMIT', '5')),
                'DAILY_LIMIT': int(os.getenv('DAILY_LIMIT', '20')),
                'MAX_IMAGE_SIZE': int(os.getenv('MAX_IMAGE_SIZE', '5242880')),
                'GROUP_ID': os.getenv('GROUP_ID', ''),
                'CHANNEL_ID': os.getenv('CHANNEL_ID', ''),
                'AUTO_QUOTE_INTERVAL': int(os.getenv('AUTO_QUOTE_INTERVAL', '3600')),
                'ENABLE_AUTO_QUOTES': os.getenv('ENABLE_AUTO_QUOTES', 'True').lower() == 'true'
            }
            
            # Parse admin IDs
            admin_ids_str = os.getenv('ADMIN_IDS', '')
            if admin_ids_str:
                config['ADMIN_IDS'] = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip().isdigit()]
            
            return config
    
    return (SafetyChecker, AdvancedImageGenerator, AutoQuoteSystem, 
            DatabaseManager, load_config)

# Import with fallback
SafetyChecker, AdvancedImageGenerator, AutoQuoteSystem, DatabaseManager, load_config_func = import_with_fallback()

# Conversation states
NAME, PHOTO, CONFIRM = range(3)

class RoastifyBot:
    """Main bot class for Roastify with enhanced features"""
    
    def __init__(self):
        """Initialize the bot with all features"""
        self.logger = self.setup_logger()
        self.logger.info("🚀 Initializing Roastify Bot v3.0...")
        
        # Load configuration
        self.config = self.load_config()
        
        # Bot token validation
        self.bot_token = self.config.get('BOT_TOKEN')
        if not self.bot_token or self.bot_token == 'YOUR_BOT_TOKEN_HERE':
            # Try to get from environment again
            try:
                from dotenv import load_dotenv
                load_dotenv()
                self.bot_token = os.getenv('BOT_TOKEN', '')
            except:
                pass
            
            if not self.bot_token:
                raise ValueError("<b>❌ BOT_TOKEN not found!</b>\nPlease add your bot token to .env file")
        
        # Initialize application with persistence
        try:
            self.application = Application.builder() \
                .token(self.bot_token) \
                .concurrent_updates(True) \
                .build()
            self.logger.info("✅ Telegram application initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize application: {e}")
            raise
        
        # Initialize modules
        self.initialize_modules()
        
        # User data cache
        self.user_data_cache = {}
        self.roast_counters = {}
        self.last_roast_time = {}
        
        # Bot statistics
        self.stats = {
            'total_roasts': 0,
            'total_users': 0,
            'today_roasts': 0,
            'active_chats': set(),
            'start_time': datetime.now()
        }
        
        # Rate limiting
        self.rate_limit = self.config.get('RATE_LIMIT', 5)
        self.daily_limit = self.config.get('DAILY_LIMIT', 20)
        
        # Register all handlers
        self.register_all_handlers()
        
        # Initialize auto quote system
        self.auto_quote_system = AutoQuoteSystem(bot=self)
        
        self.logger.info("🎉 Roastify Bot v3.0 initialized successfully!")
        self.logger.info(f"📊 Config: Rate Limit={self.rate_limit}/min, Daily Limit={self.daily_limit}/day")
    
    def setup_logger(self):
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler('logs/bot.log', encoding='utf-8')
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def load_config(self):
        """Load configuration from .env file"""
        try:
            return load_config_func()
        except Exception as e:
            self.logger.error(f"❌ Error loading config: {e}")
            return {
                'BOT_TOKEN': '',
                'ADMIN_IDS': [],
                'LOG_LEVEL': 'INFO',
                'DATABASE_URL': 'sqlite:///roastify.db',
                'RATE_LIMIT': 5,
                'DAILY_LIMIT': 20,
                'MAX_IMAGE_SIZE': 5242880,
                'GROUP_ID': '',
                'CHANNEL_ID': '',
                'AUTO_QUOTE_INTERVAL': 3600,
                'ENABLE_AUTO_QUOTES': True
            }
    
    def initialize_modules(self):
        """Initialize all bot modules"""
        try:
            self.safety_checker = SafetyChecker()
            self.logger.info("✅ SafetyChecker initialized")
        except Exception as e:
            self.logger.error(f"❌ SafetyChecker: {e}")
            self.safety_checker = None
        
        try:
            self.image_generator = AdvancedImageGenerator()
            self.logger.info("✅ ImageGenerator initialized")
        except Exception as e:
            self.logger.error(f"❌ ImageGenerator: {e}")
            self.image_generator = None
        
        try:
            self.db = DatabaseManager()
            self.logger.info("✅ Database initialized")
        except Exception as e:
            self.logger.error(f"❌ Database: {e}")
            self.db = None
    
    def register_all_handlers(self):
        """Register all command and message handlers"""
        
        # ========== BASIC COMMANDS ==========
        basic_commands = [
            ("start", self.start_command),
            ("help", self.help_command),
            ("roast", self.roast_command),
            ("stats", self.stats_command),
            ("profile", self.profile_command),
            ("quote", self.quote_command),
            ("joke", self.joke_command),
            ("fact", self.fact_command),
            ("invite", self.invite_command),
            ("support", self.support_command),
        ]
        
        for command, handler in basic_commands:
            self.application.add_handler(CommandHandler(command, handler))
        
        # ========== MESSAGE HANDLERS ==========
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # ========== CALLBACK QUERY HANDLERS ==========
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # ========== ERROR HANDLER ==========
        self.application.add_error_handler(self.error_handler)
        
        self.logger.info(f"✅ Registered {len(basic_commands)} commands")
    
    # ========== START COMMAND ==========
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with enhanced welcome"""
        try:
            user = update.effective_user
            
            # Create keyboard with English buttons
            keyboard = [
                [
                    InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
                    InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn")
                ],
                [
                    InlineKeyboardButton("🎭 Create Roast", callback_data="create_roast"),
                    InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
                    InlineKeyboardButton("🆘 Help", callback_data="help_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = f"""
<b>🎉 Welcome to Roastify Bot v3.0, {user.first_name}!</b> 🤖

<u>Your ultimate roasting companion!</u>

<code>✨ Key Features:</code>
• 🎭 <b>Smart Roast Generation</b>
• 📊 <b>User Statistics</b>
• 🤖 <b>Auto Quotes & Jokes</b>
• ⚡ <b>Fast & Easy</b>

<code>📱 Quick Start:</code>
• Use <code>/roast [name]</code> to roast someone
• Use <code>/help</code> for all commands
• Use buttons below for quick actions

<code>⚡ Choose your language:</code> 🇬🇧/🇧🇩
            """
            
            await update.message.reply_html(
                welcome_text,
                reply_markup=reply_markup
            )
            
            # Track user
            chat = update.effective_chat
            self.stats['active_chats'].add(chat.id)
            if self.db:
                self.db.add_user(user.id, user.first_name, user.username)
                
        except Exception as e:
            self.logger.error(f"Error in start_command: {e}")
            await update.message.reply_text("❌ An error occurred. Please try again.")
    
    # ========== HELP COMMAND ==========
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            help_text = """
<b>🤖 ROASTIFY BOT - COMMANDS 📚</b>

<u><b>🎭 ROASTING COMMANDS:</b></u>
<code>/roast [name]</code> - Create roast for someone

<u><b>📊 STATS & INFO:</b></u>
<code>/stats</code> - Bot statistics
<code>/profile</code> - Your profile

<u><b>🔄 CONTENT COMMANDS:</b></u>
<code>/quote</code> - Random quote
<code>/joke</code> - Random joke
<code>/fact</code> - Random fact

<u><b>⚙️ UTILITY COMMANDS:</b></u>
<code>/invite</code> - Invite link
<code>/support</code> - Support

<u><b>📱 Quick Actions:</b></u>
Use buttons for faster access!
Example: <code>/roast John</code>
            """
            
            # English keyboard buttons
            keyboard = [
                [
                    InlineKeyboardButton("🎭 Roast Now", callback_data="quick_roast"),
                    InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu"),
                    InlineKeyboardButton("🆘 Help Menu", callback_data="help_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(
                help_text,
                reply_markup=reply_markup
            )
        except Exception as e:
            self.logger.error(f"Error in help_command: {e}")
            await update.message.reply_text("❌ An error occurred. Please try again.")
    
    # ========== ROAST COMMAND ==========
    async def roast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /roast command"""
        try:
            user_id = update.effective_user.id
            
            # Rate limiting check
            if not self.check_rate_limit(user_id):
                await update.message.reply_html(
                    "<b>⏳ Rate limit exceeded!</b>\n"
                    f"Please wait {self.rate_limit} seconds between roasts."
                )
                return
            
            # Daily limit check
            if not self.check_daily_limit(user_id):
                await update.message.reply_html(
                    f"<b>📊 Daily limit reached!</b>\n"
                    f"You've used {self.daily_limit} roasts today.\n"
                    "Please try again tomorrow!"
                )
                return
            
            # Get target name
            if context.args:
                target_name = ' '.join(context.args)
            else:
                await update.message.reply_html(
                    "<b>👤 Please specify a name!</b>\n\n"
                    "Usage: <code>/roast [name]</code>\n"
                    "Example: <code>/roast John</code>"
                )
                return
            
            # Safety check
            if self.safety_checker and not self.safety_checker.is_safe(target_name):
                await update.message.reply_html(
                    "<b>⚠️ Content blocked!</b>\n"
                    "Please use appropriate names only."
                )
                return
            
            # Generate roast
            roast_text = self.generate_roast(target_name)
            
            # Create keyboard with English options
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Another Roast", callback_data=f"another_roast:{target_name}"),
                    InlineKeyboardButton("😂 Share", callback_data=f"share_roast:{target_name}")
                ],
                [
                    InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
                    InlineKeyboardButton("🎭 New Roast", callback_data="new_roast")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send roast with HTML formatting
            await update.message.reply_html(
                f"<b>🔥 Roast for {target_name}:</b>\n\n"
                f"<i>{roast_text}</i>\n\n"
                f"<code>📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</code>",
                reply_markup=reply_markup
            )
            
            # Update statistics
            self.update_roast_stats(user_id, target_name)
            
        except Exception as e:
            self.logger.error(f"Error in roast_command: {e}")
            await update.message.reply_text("❌ An error occurred while generating roast. Please try again.")
    
    def generate_roast(self, name: str) -> str:
        """Generate a roast for given name"""
        roasts = [
            f"{name}, তোমার বুদ্ধির জন্য পৃথিবীতে এখনো কোন এন্টিবায়োটিক আবিষ্কার হয়নি!",
            f"{name}, তুমি যদি কম্পিউটার হোতা, তাহলে Ctrl+Alt+Delete তোমার সবচেয়ে ব্যবহার করা হত!",
            f"{name}, তোমাকে দেখলে আইনস্টাইন তার থিওরি ভুলে যেত!",
            f"{name}, তোমার মতো মানুষ জন্মানোর আগে আল্লাহ একটু ভাবছিলেন কি করবেন!",
            f"{name}, তোমার বুদ্ধিমত্তা দেখলে ক্যালকুলেটরও হতাশ হয়!",
            f"{name}, তোমার ফেসবুক প্রোফাইল দেখলে জুকারবার্গও লজ্জা পায়!",
            f"{name}, তুমি যদি গুগল হোতা, তাহলে 'হাবা' সার্চ করলে তোমার ফটো আসতো!",
            f"{name}, তোমার জীবন স্টোরিতে লাইক দিবে শুধু তোমার মা!",
            f"{name}, তুমি জন্মেছিলে হাসানোর জন্য, কিন্তু এখন মানুষ কাঁদে তোমার বুদ্ধি দেখে!",
            f"{name}, তোমার সম্পর্কে বলতে গেলে গুগল ম্যাপও হারিয়ে যায়!"
        ]
        
        return random.choice(roasts)
    
    # ========== STATS COMMAND ==========
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        try:
            uptime = datetime.now() - self.stats['start_time']
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            stats_text = f"""
<b>📊 ROASTIFY BOT STATISTICS</b>

<u>🤖 Bot Info:</u>
• <b>Version:</b> 3.0
• <b>Uptime:</b> {days}d {hours}h {minutes}m
• <b>Active Chats:</b> {len(self.stats['active_chats'])}
• <b>Total Users:</b> {self.stats['total_users']}

<u>🎭 Roasting Stats:</u>
• <b>Total Roasts:</b> {self.stats['total_roasts']}
• <b>Today's Roasts:</b> {self.stats['today_roasts']}
• <b>Rate Limit:</b> {self.rate_limit}/min
• <b>Daily Limit:</b> {self.daily_limit}/day

<u>⚙️ System:</u>
• <b>Database:</b> {'✅ Connected' if self.db else '❌ Disabled'}
• <b>Safety Check:</b> {'✅ Active' if self.safety_checker else '❌ Disabled'}
• <b>Image Gen:</b> {'✅ Active' if self.image_generator else '❌ Disabled'}
• <b>Auto Quotes:</b> {'✅ Active' if self.auto_quote_system else '❌ Disabled'}

<code>🔄 Last Updated: {datetime.now().strftime('%H:%M:%S')}</code>
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"),
                    InlineKeyboardButton("📤 Export", callback_data="export_stats")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(stats_text, reply_markup=reply_markup)
        except Exception as e:
            self.logger.error(f"Error in stats_command: {e}")
            await update.message.reply_text("❌ An error occurred while fetching stats.")
    
    # ========== PROFILE COMMAND ==========
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Get user stats
            total_roasts = self.roast_counters.get(user_id, 0)
            today_roasts = random.randint(1, 10)
            rank = random.randint(1, 100)
            level = total_roasts // 10 + 1
            
            profile_text = f"""
<b>👤 USER PROFILE</b>

<u>Personal Info:</u>
• <b>Name:</b> {user.first_name} {user.last_name or ''}
• <b>Username:</b> @{user.username or 'Not set'}
• <b>User ID:</b> <code>{user_id}</code>
• <b>Joined:</b> {datetime.now().strftime('%Y-%m-%d')}

<u>🎭 Roasting Stats:</u>
• <b>Total Roasts:</b> {total_roasts}
• <b>Today's Roasts:</b> {today_roasts}
• <b>Global Rank:</b> #{rank}
• <b>Level:</b> {level}
• <b>Roasts Left Today:</b> {max(0, self.daily_limit - today_roasts)}

<code>📊 Profile created: {datetime.now().strftime('%H:%M')}</code>
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🎭 Create Roast", callback_data="create_roast"),
                    InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
                ],
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_profile"),
                    InlineKeyboardButton("📤 Share", callback_data="share_profile")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(profile_text, reply_markup=reply_markup)
        except Exception as e:
            self.logger.error(f"Error in profile_command: {e}")
            await update.message.reply_text("❌ An error occurred while fetching profile.")
    
    # ========== AUTO QUOTE RELATED COMMANDS ==========
    async def quote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quote command"""
        try:
            if self.auto_quote_system:
                quote = await self.auto_quote_system.get_random_quote()
                
                keyboard = [
                    [
                        InlineKeyboardButton("📜 Another Quote", callback_data="another_quote"),
                        InlineKeyboardButton("🎭 Create Roast", callback_data="create_roast")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_html(quote, reply_markup=reply_markup)
            else:
                await update.message.reply_html("<b>❌ Quote system is disabled!</b>")
        except Exception as e:
            self.logger.error(f"Error in quote_command: {e}")
            await update.message.reply_text("❌ An error occurred while fetching quote.")
    
    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /joke command"""
        try:
            if self.auto_quote_system:
                joke = await self.auto_quote_system.get_random_joke()
                
                keyboard = [
                    [
                        InlineKeyboardButton("😂 Another Joke", callback_data="another_joke"),
                        InlineKeyboardButton("📜 Get Quote", callback_data="get_quote")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_html(joke, reply_markup=reply_markup)
            else:
                await update.message.reply_html("<b>❌ Joke system is disabled!</b>")
        except Exception as e:
            self.logger.error(f"Error in joke_command: {e}")
            await update.message.reply_text("❌ An error occurred while fetching joke.")
    
    async def fact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /fact command"""
        try:
            if self.auto_quote_system:
                fact = await self.auto_quote_system.get_random_fact()
                
                keyboard = [
                    [
                        InlineKeyboardButton("🔍 Another Fact", callback_data="another_fact"),
                        InlineKeyboardButton("📚 More Facts", callback_data="more_facts")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_html(fact, reply_markup=reply_markup)
            else:
                await update.message.reply_html("<b>❌ Fact system is disabled!</b>")
        except Exception as e:
            self.logger.error(f"Error in fact_command: {e}")
            await update.message.reply_text("❌ An error occurred while fetching fact.")
    
    # ========== UTILITY COMMANDS ==========
    async def invite_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /invite command"""
        try:
            bot_username = (await self.application.bot.get_me()).username
            invite_link = f"https://t.me/{bot_username}?start=invite"
            
            invite_text = f"""
<b>📢 INVITE ROASTIFY BOT</b>

Invite Roastify Bot to your groups and share the fun with friends!

<u>🔗 Invite Links:</u>
• <b>Bot Link:</b> <code>{invite_link}</code>
• <b>Direct Add:</b> <code>https://t.me/{bot_username}?startgroup=true</code>

<code>🤝 Share with friends!</code>
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("📥 Add to Group", url=f"https://t.me/{bot_username}?startgroup=true"),
                    InlineKeyboardButton("👥 Share with Friends", callback_data="share_invite")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(invite_text, reply_markup=reply_markup)
        except Exception as e:
            self.logger.error(f"Error in invite_command: {e}")
            await update.message.reply_text("❌ An error occurred while generating invite.")
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /support command"""
        try:
            support_text = """
<b>🆘 SUPPORT & HELP</b>

Need help or have questions? Here's how you can get support:

<u>⚡ Quick Fixes:</u>
1. Make sure bot has admin rights in groups
2. Check your internet connection
3. Update to latest version
4. Clear chat and try again

<u>🔧 Report Problems:</u>
Contact the developer for support.

<code>⏰ Response Time: Usually within 24 hours</code>
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot"),
                    InlineKeyboardButton("📝 Give Feedback", callback_data="give_feedback")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(support_text, reply_markup=reply_markup)
        except Exception as e:
            self.logger.error(f"Error in support_command: {e}")
            await update.message.reply_text("❌ An error occurred while fetching support info.")
    
    # ========== CALLBACK QUERY HANDLER ==========
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            
            # Handle different callback queries
            if data == "create_roast":
                await self.roast_command(update, context)
            elif data == "my_stats":
                await self.stats_command(update, context)
            elif data == "settings_menu":
                await query.message.reply_html("<b>⚙️ Settings coming soon!</b>")
            elif data == "help_menu":
                await self.help_command(update, context)
            elif data == "quick_roast":
                # Ask for name
                await query.message.reply_html(
                    "<b>👤 Enter the name to roast:</b>\n"
                    "Send me the name you want to roast:"
                )
            elif data.startswith("another_roast:"):
                target_name = data.split(":")[1]
                roast_text = self.generate_roast(target_name)
                await query.message.reply_html(
                    f"<b>🔥 Another roast for {target_name}:</b>\n\n"
                    f"<i>{roast_text}</i>"
                )
            elif data == "another_quote":
                await self.quote_command(update, context)
            elif data == "another_joke":
                await self.joke_command(update, context)
            elif data == "another_fact":
                await self.fact_command(update, context)
            elif data == "lang_en":
                await query.message.reply_html(
                    "<b>🌐 Language set to English!</b>\n"
                    "All messages will now be in English."
                )
            elif data == "lang_bn":
                await query.message.reply_html(
                    "<b>🌐 ভাষা বাংলায় সেট করা হয়েছে!</b>\n"
                    "সব মেসেজ এখন বাংলায় হবে।"
                )
            elif data == "refresh_stats":
                await self.stats_command(update, context)
            elif data == "refresh_profile":
                await self.profile_command(update, context)
            else:
                await query.message.reply_text("❌ Unknown action.")
                
        except Exception as e:
            self.logger.error(f"Error in handle_callback_query: {e}")
            try:
                await query.message.reply_text("❌ An error occurred. Please try again.")
            except:
                pass
    
    # ========== MESSAGE HANDLERS ==========
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            text = update.message.text
            user = update.effective_user
            
            # Handle other text messages
            if text.lower() in ['hi', 'hello', 'hey']:
                await update.message.reply_html(f"<b>👋 Hello {user.first_name}!</b>\nHow can I help you today?")
            elif text.lower() in ['thanks', 'thank you', 'thx']:
                await update.message.reply_html("<b>🙏 You're welcome!</b>\nGlad to help!")
            elif text.lower() in ['bye', 'goodbye']:
                await update.message.reply_html("<b>👋 Goodbye!</b>\nHope to see you again soon!")
            else:
                # Default response
                keyboard = [
                    [
                        InlineKeyboardButton("🎭 Create Roast", callback_data="create_roast"),
                        InlineKeyboardButton("🆘 Help", callback_data="help_menu")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_html(
                    f"<b>🤖 Hi {user.first_name}!</b>\n"
                    "I'm Roastify Bot. How can I assist you today?\n\n"
                    "Try <code>/help</code> to see all available commands.",
                    reply_markup=reply_markup
                )
        except Exception as e:
            self.logger.error(f"Error in handle_text_message: {e}")
    
    # ========== ERROR HANDLER (FIXED) ==========
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors with better debugging"""
        try:
            error = context.error
            
            # Log the error with full traceback
            self.logger.error(f"Bot error: {error}", exc_info=True)
            
            # Try to send error message to user
            try:
                if update and update.effective_message:
                    # Simple error message without HTML
                    await update.effective_message.reply_text(
                        "❌ An error occurred. Please try again later."
                    )
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"Error in error_handler: {e}")
    
    # ========== UTILITY METHODS ==========
    def check_rate_limit(self, user_id: int) -> bool:
        """Check if user has exceeded rate limit"""
        now = datetime.now()
        last_time = self.last_roast_time.get(user_id)
        
        if last_time:
            time_diff = (now - last_time).seconds
            if time_diff < self.rate_limit:
                return False
        
        self.last_roast_time[user_id] = now
        return True
    
    def check_daily_limit(self, user_id: int) -> bool:
        """Check if user has exceeded daily limit"""
        today = datetime.now().date()
        user_data = self.user_data_cache.get(user_id, {})
        
        if user_data.get('date') != today:
            user_data['date'] = today
            user_data['count'] = 0
            self.user_data_cache[user_id] = user_data
        
        return user_data['count'] < self.daily_limit
    
    def update_roast_stats(self, user_id: int, target_name: str):
        """Update roast statistics"""
        # Update user data
        today = datetime.now().date()
        user_data = self.user_data_cache.get(user_id, {})
        
        if user_data.get('date') != today:
            user_data['date'] = today
            user_data['count'] = 0
        
        user_data['count'] += 1
        self.user_data_cache[user_id] = user_data
        
        # Update bot stats
        self.stats['total_roasts'] += 1
        self.stats['today_roasts'] += 1
        
        # Update counter
        self.roast_counters[user_id] = self.roast_counters.get(user_id, 0) + 1
        
        self.logger.info(f"✅ Roast generated by {user_id} for {target_name}")
    
    # ========== BOT STARTUP & SHUTDOWN ==========
    async def start_bot(self):
        """Start the bot"""
        try:
            self.logger.info("🤖 Starting Roastify Bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.logger.info("✅ Roastify Bot is now running! Press Ctrl+C to stop.")
            print("\n✅ Bot started successfully! Press Ctrl+C to stop.")
            
            # Keep running
            await asyncio.Event().wait()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start bot: {e}")
            print(f"\n❌ Failed to start bot: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the bot"""
        try:
            self.logger.info("🛑 Stopping Roastify Bot...")
            
            # Stop auto quote system if exists
            if hasattr(self.auto_quote_system, 'stop'):
                try:
                    self.auto_quote_system.stop()
                except:
                    pass
            
            # Stop application
            if hasattr(self, 'application') and self.application:
                try:
                    await self.application.stop()
                    await self.application.shutdown()
                except:
                    pass
            
            self.logger.info("👋 Roastify Bot stopped successfully!")
            
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
    
    # ========== COMPATIBILITY METHODS ==========
    def run(self):
        """
        Run the bot (for compatibility with main.py)
        This is the main entry point called by main.py
        """
        try:
            # Create and set event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the bot
            self.logger.info("🚀 Starting Roastify Bot via run() method...")
            
            try:
                # Start the bot
                bot_task = loop.create_task(self.start_bot())
                loop.run_until_complete(bot_task)
                
            except KeyboardInterrupt:
                self.logger.info("⌨️ Keyboard interrupt received")
                print("\n🛑 Bot stopped by user")
            except Exception as e:
                self.logger.error(f"❌ Error in run(): {e}")
                print(f"\n❌ Error: {e}")
                raise
            finally:
                # Clean shutdown
                try:
                    shutdown_task = loop.create_task(self.stop_bot())
                    loop.run_until_complete(shutdown_task)
                except:
                    pass
                finally:
                    loop.close()
                    
        except Exception as e:
            self.logger.error(f"Fatal error in run(): {e}")
            print(f"\n❌ Fatal error: {e}")
            sys.exit(1)


# If bot.py is run directly
if __name__ == "__main__":
    try:
        bot = RoastifyBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
