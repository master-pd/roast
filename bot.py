#!/usr/bin/env python3
"""
Roastify Bot - Main Bot File (Fully Fixed)
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

# ========== MODULE IMPORT WITH WORKING FALLBACK ==========
def import_with_fallback():
    """Import modules with working fallback classes"""
    
    # SafetyChecker - FIXED VERSION
    try:
        from safety_checker import SafetyChecker
        safety_checker_class = SafetyChecker
    except ImportError:
        class SafetyChecker:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.logger.info("✅ Using fallback SafetyChecker")
                self.banned_words = ["fuck", "shit", "asshole", "গালি", "অপমান", "অশ্লীল"]
            
            def is_safe(self, text, user_id=None):
                """Check if text is safe - FIXED METHOD"""
                if not text:
                    return False
                text_lower = text.lower()
                for word in self.banned_words:
                    if word in text_lower:
                        self.logger.warning(f"Banned word detected: {word}")
                        return False
                return True
            
            def analyze_message(self, text, user_id=None):
                """Analyze message safety"""
                return {"is_safe": True, "score": 100, "warnings": []}
        
        safety_checker_class = SafetyChecker
    
    # ImageGenerator
    try:
        from image_generator import AdvancedImageGenerator
        image_generator_class = AdvancedImageGenerator
    except ImportError:
        class AdvancedImageGenerator:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.logger.info("✅ Using fallback ImageGenerator")
            
            def generate_roast_image(self, roast_text, name, style="default"):
                self.logger.info(f"📸 Would generate image for {name}")
                return None
        
        image_generator_class = AdvancedImageGenerator
    
    # AutoQuoteSystem
    try:
        from auto_quote import AutoQuoteSystem
        auto_quote_class = AutoQuoteSystem
    except ImportError:
        class AutoQuoteSystem:
            def __init__(self, bot=None):
                self.bot = bot
                self.logger = logging.getLogger(__name__)
                self.logger.info("✅ Using fallback AutoQuoteSystem")
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
                """Get random quote"""
                quote = random.choice(self.quotes)
                return f"<b>📜 Quote of the Day:</b>\n\n<i>\"{quote}\"</i>"
            
            async def get_random_joke(self):
                """Get random joke"""
                joke = random.choice(self.jokes)
                return f"<b>😂 Funny Joke:</b>\n\n{joke}"
            
            async def get_random_fact(self):
                """Get random fact"""
                fact = random.choice(self.facts)
                return f"<b>🔍 Did You Know?</b>\n\n{fact}"
        
        auto_quote_class = AutoQuoteSystem
    
    # DatabaseManager
    try:
        from database import DatabaseManager
        database_class = DatabaseManager
    except ImportError:
        class DatabaseManager:
            def __init__(self):
                self.logger = logging.getLogger(__name__)
                self.logger.info("✅ Using fallback DatabaseManager")
                self.users = {}
                self.roasts = []
            
            def add_user(self, user_id, first_name, username=None):
                """Add user to database"""
                self.users[user_id] = {
                    "name": first_name, 
                    "username": username,
                    "joined": datetime.now()
                }
                return True
            
            def get_user_stats(self, user_id):
                """Get user statistics"""
                return {"roast_count": 0, "rank": 100, "level": 1}
        
        database_class = DatabaseManager
    
    # Config Loader
    def load_config_function():
        """Load configuration"""
        try:
            from config_loader import load_config
            return load_config()
        except ImportError:
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
                try:
                    config['ADMIN_IDS'] = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip().isdigit()]
                except:
                    config['ADMIN_IDS'] = []
            
            return config
    
    return (safety_checker_class, image_generator_class, auto_quote_class, 
            database_class, load_config_function)

# Import with fallback
SafetyChecker, AdvancedImageGenerator, AutoQuoteSystem, DatabaseManager, load_config_func = import_with_fallback()

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
                load_dotenv()
                self.bot_token = os.getenv('BOT_TOKEN', '')
            except:
                pass
            
            if not self.bot_token:
                raise ValueError("❌ BOT_TOKEN not found! Please add your bot token to .env file")
        
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
            # Create minimal safety checker
            class MinimalSafetyChecker:
                def is_safe(self, text, user_id=None):
                    return True if text and len(text) > 1 else False
            self.safety_checker = MinimalSafetyChecker()
        
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
    
    # ========== COMMAND HANDLERS ==========
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            message = update.message or update.callback_query.message
            
            keyboard = [
                [InlineKeyboardButton("🎭 Create Roast", callback_data="create_roast")],
                [InlineKeyboardButton("📊 My Stats", callback_data="my_stats")],
                [InlineKeyboardButton("🆘 Help", callback_data="help_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = f"""
<b>🎉 Welcome to Roastify Bot, {user.first_name}!</b> 🤖

Use <code>/roast [name]</code> to roast someone.

Example: <code>/roast John</code>
            """
            
            await message.reply_html(welcome_text, reply_markup=reply_markup)
            
        except Exception as e:
            self.logger.error(f"Error in start_command: {e}")
            try:
                await update.message.reply_text("Welcome! Use /help for commands.")
            except:
                pass
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            message = update.message or update.callback_query.message
            
            help_text = """
<b>🤖 ROASTIFY BOT COMMANDS</b>

• <code>/start</code> - Start the bot
• <code>/help</code> - Show this help
• <code>/roast [name]</code> - Roast someone
• <code>/stats</code> - Bot statistics
• <code>/profile</code> - Your profile
• <code>/quote</code> - Random quote
• <code>/joke</code> - Random joke
• <code>/fact</code> - Random fact
• <code>/invite</code> - Invite link
• <code>/support</code> - Support

<b>Example:</b> <code>/roast John</code>
            """
            
            await message.reply_html(help_text)
            
        except Exception as e:
            self.logger.error(f"Error in help_command: {e}")
    
    async def roast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /roast command"""
        try:
            user_id = update.effective_user.id
            message = update.message or update.callback_query.message
            
            # Get target name
            if context.args:
                target_name = ' '.join(context.args)
            else:
                await message.reply_text("Please specify a name!\nUsage: /roast [name]\nExample: /roast John")
                return
            
            # Safety check
            if self.safety_checker:
                try:
                    if not self.safety_checker.is_safe(target_name):
                        await message.reply_text("⚠️ Please use appropriate names only.")
                        return
                except AttributeError:
                    # is_safe method might not exist
                    pass
            
            # Generate roast
            roast_text = self.generate_roast(target_name)
            
            # Create keyboard
            keyboard = [
                [InlineKeyboardButton("🔄 Another", callback_data=f"another:{target_name}")],
                [InlineKeyboardButton("📊 Stats", callback_data="my_stats")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send roast
            await message.reply_html(
                f"<b>🔥 Roast for {target_name}:</b>\n\n"
                f"<i>{roast_text}</i>",
                reply_markup=reply_markup
            )
            
            # Update statistics
            self.update_roast_stats(user_id, target_name)
            
        except Exception as e:
            self.logger.error(f"Error in roast_command: {e}")
            try:
                message = update.message or update.callback_query.message
                await message.reply_text("❌ Error generating roast. Please try again.")
            except:
                pass
    
    def generate_roast(self, name: str) -> str:
        """Generate a roast for given name"""
        roasts = [
            f"{name}, তোমার বুদ্ধির জন্য পৃথিবীতে এখনো কোন এন্টিবায়োটিক আবিষ্কার হয়নি!",
            f"{name}, তুমি যদি কম্পিউটার হোতা, তাহলে Ctrl+Alt+Delete তোমার সবচেয়ে ব্যবহার করা হত!",
            f"{name}, তোমাকে দেখলে আইনস্টাইন তার থিওরি ভুলে যেত!",
            f"{name}, তোমার মতো মানুষ জন্মানোর আগে আল্লাহ একটু ভাবছিলেন কি করবেন!",
            f"{name}, তোমার বুদ্ধিমত্তা দেখলে ক্যালকুলেটরও হতাশ হয়!",
        ]
        return random.choice(roasts)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        try:
            message = update.message or update.callback_query.message
            
            uptime = datetime.now() - self.stats['start_time']
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            stats_text = f"""
<b>📊 BOT STATISTICS</b>

• <b>Version:</b> 3.0
• <b>Uptime:</b> {days}d {hours}h {minutes}m
• <b>Total Roasts:</b> {self.stats['total_roasts']}
• <b>Today's Roasts:</b> {self.stats['today_roasts']}
• <b>Active Chats:</b> {len(self.stats['active_chats'])}
• <b>Rate Limit:</b> {self.rate_limit}/min
• <b>Daily Limit:</b> {self.daily_limit}/day
            """
            
            await message.reply_html(stats_text)
            
        except Exception as e:
            self.logger.error(f"Error in stats_command: {e}")
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        try:
            user = update.effective_user
            message = update.message or update.callback_query.message
            
            total_roasts = self.roast_counters.get(user.id, 0)
            
            profile_text = f"""
<b>👤 YOUR PROFILE</b>

• <b>Name:</b> {user.first_name}
• <b>Username:</b> @{user.username or 'N/A'}
• <b>User ID:</b> <code>{user.id}</code>
• <b>Total Roasts:</b> {total_roasts}
• <b>Level:</b> {total_roasts // 10 + 1}
            """
            
            await message.reply_html(profile_text)
            
        except Exception as e:
            self.logger.error(f"Error in profile_command: {e}")
    
    async def quote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quote command"""
        try:
            message = update.message or update.callback_query.message
            
            if self.auto_quote_system:
                quote = await self.auto_quote_system.get_random_quote()
                await message.reply_html(quote)
            else:
                await message.reply_text("Random quote: Life is beautiful!")
                
        except Exception as e:
            self.logger.error(f"Error in quote_command: {e}")
            try:
                await message.reply_text("Random quote: Life is beautiful!")
            except:
                pass
    
    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /joke command"""
        try:
            message = update.message or update.callback_query.message
            
            if self.auto_quote_system:
                joke = await self.auto_quote_system.get_random_joke()
                await message.reply_html(joke)
            else:
                jokes = [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "What do you call a fake noodle? An impasta!"
                ]
                await message.reply_text(random.choice(jokes))
                
        except Exception as e:
            self.logger.error(f"Error in joke_command: {e}")
    
    async def fact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /fact command"""
        try:
            message = update.message or update.callback_query.message
            
            if self.auto_quote_system:
                fact = await self.auto_quote_system.get_random_fact()
                await message.reply_html(fact)
            else:
                facts = [
                    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat.",
                    "Octopuses have three hearts."
                ]
                await message.reply_text(random.choice(facts))
                
        except Exception as e:
            self.logger.error(f"Error in fact_command: {e}")
    
    async def invite_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /invite command"""
        try:
            message = update.message or update.callback_query.message
            bot_username = (await self.application.bot.get_me()).username
            
            invite_text = f"""
<b>📢 INVITE THIS BOT</b>

Add me to your groups:
https://t.me/{bot_username}?startgroup=true

Share with friends!
            """
            
            await message.reply_html(invite_text)
            
        except Exception as e:
            self.logger.error(f"Error in invite_command: {e}")
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /support command"""
        try:
            message = update.message or update.callback_query.message
            
            support_text = """
<b>🆘 SUPPORT</b>

Need help? Contact the developer.

Common issues:
1. Bot not responding? Try /start
2. Commands not working? Check /help
3. Rate limited? Wait a few seconds
            """
            
            await message.reply_html(support_text)
            
        except Exception as e:
            self.logger.error(f"Error in support_command: {e}")
    
    # ========== CALLBACK QUERY HANDLER ==========
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            
            if data == "create_roast":
                await query.message.reply_text("Send me a name to roast!\nExample: John")
            elif data == "my_stats":
                await self.stats_command(update, context)
            elif data == "help_menu":
                await self.help_command(update, context)
            elif data.startswith("another:"):
                target_name = data.split(":", 1)[1]
                roast_text = self.generate_roast(target_name)
                await query.message.reply_html(
                    f"<b>Another roast for {target_name}:</b>\n\n"
                    f"<i>{roast_text}</i>"
                )
            else:
                await query.message.reply_text("✅ Action completed!")
                
        except Exception as e:
            self.logger.error(f"Error in handle_callback_query: {e}")
            try:
                await query.answer("❌ Error processing request")
            except:
                pass
    
    # ========== MESSAGE HANDLER ==========
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            text = update.message.text
            user = update.effective_user
            
            if text.lower() in ['hi', 'hello', 'hey']:
                await update.message.reply_text(f"👋 Hello {user.first_name}! Use /help for commands.")
            elif 'roast' in text.lower():
                await update.message.reply_text("Use /roast [name] to roast someone!\nExample: /roast John")
            else:
                await update.message.reply_text(f"Hi {user.first_name}! I'm Roastify Bot. Use /help for commands.")
                
        except Exception as e:
            self.logger.error(f"Error in handle_text_message: {e}")
    
    # ========== ERROR HANDLER ==========
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        try:
            error = context.error
            self.logger.error(f"Bot error: {error}")
            
            # Don't send error message to users
            # Just log it
            
        except Exception as e:
            self.logger.error(f"Error in error_handler: {e}")
    
    # ========== UTILITY METHODS ==========
    def update_roast_stats(self, user_id: int, target_name: str):
        """Update roast statistics"""
        try:
            # Update user data
            today = datetime.now().date()
            if user_id not in self.user_data_cache:
                self.user_data_cache[user_id] = {'date': today, 'count': 0}
            
            user_data = self.user_data_cache[user_id]
            if user_data.get('date') != today:
                user_data['date'] = today
                user_data['count'] = 0
            
            user_data['count'] += 1
            
            # Update bot stats
            self.stats['total_roasts'] += 1
            self.stats['today_roasts'] += 1
            self.roast_counters[user_id] = self.roast_counters.get(user_id, 0) + 1
            
            self.logger.info(f"Roast generated by {user_id} for {target_name}")
            
        except Exception as e:
            self.logger.error(f"Error updating stats: {e}")
    
    # ========== BOT CONTROL ==========
    async def start_bot(self):
        """Start the bot"""
        try:
            self.logger.info("🤖 Starting Roastify Bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.logger.info("✅ Bot is now running! Press Ctrl+C to stop.")
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
            self.logger.info("🛑 Stopping bot...")
            
            if hasattr(self, 'application') and self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            self.logger.info("👋 Bot stopped successfully!")
            
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
    
    def run(self):
        """Run the bot (for main.py)"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.logger.info("🚀 Starting bot via run()...")
            
            try:
                loop.run_until_complete(self.start_bot())
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
            finally:
                try:
                    loop.run_until_complete(self.stop_bot())
                finally:
                    loop.close()
                    
        except Exception as e:
            self.logger.error(f"Fatal error in run(): {e}")
            print(f"\n❌ Fatal error: {e}")
            sys.exit(1)


# Direct execution
if __name__ == "__main__":
    try:
        bot = RoastifyBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
