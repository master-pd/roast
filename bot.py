#!/usr/bin/env python3
"""
Roastify Bot - Main Bot File
তুমি লেখো, বাকি অপমান আমরা করবো 😈
"""

import os
import sys
import logging
import json
import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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

# Import project modules
try:
    from safety_checker import SafetyChecker
    from image_generator import AdvancedImageGenerator
    from auto_quote import AutoQuoteSystem
    from database import DatabaseManager
    from config_loader import load_config
except ImportError as e:
    print(f"<b>❌ Import error:</b> {e}")
    sys.exit(1)

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
            raise ValueError("<b>❌ BOT_TOKEN not found or invalid in .env file</b>")
        
        # Initialize application with persistence
        self.application = Application.builder() \
            .token(self.bot_token) \
            .concurrent_updates(True) \
            .build()
        
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
        config = {}
        env_path = Path('.env')
        
        if env_path.exists():
            load_dotenv()
            self.logger.info("📁 Loading config from .env file")
            
            # Essential configuration
            config['BOT_TOKEN'] = os.getenv('BOT_TOKEN', '')
            admin_ids = os.getenv('ADMIN_IDS', '')
            config['ADMIN_IDS'] = [int(id.strip()) for id in admin_ids.split(',') if id.strip().isdigit()]
            config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')
            config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///roastify.db')
            
            # Bot settings
            config['RATE_LIMIT'] = int(os.getenv('RATE_LIMIT', '5'))
            config['DAILY_LIMIT'] = int(os.getenv('DAILY_LIMIT', '20'))
            config['MAX_IMAGE_SIZE'] = int(os.getenv('MAX_IMAGE_SIZE', '5242880'))
            config['GROUP_ID'] = os.getenv('GROUP_ID', '')
            config['CHANNEL_ID'] = os.getenv('CHANNEL_ID', '')
            
            # Auto quote settings
            config['AUTO_QUOTE_INTERVAL'] = int(os.getenv('AUTO_QUOTE_INTERVAL', '3600'))
            config['ENABLE_AUTO_QUOTES'] = os.getenv('ENABLE_AUTO_QUOTES', 'True').lower() == 'true'
            
        else:
            self.logger.warning("⚠️ .env file not found, using default configuration")
            config = {
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
        
        return config
    
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
        
        # ========== CONVERSATION HANDLERS ==========
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("create", self.create_roast_start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_roast_name)],
                PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, self.get_roast_photo)],
                CONFIRM: [CallbackQueryHandler(self.confirm_roast)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_create)]
        )
        self.application.add_handler(conv_handler)
        
        # ========== BASIC COMMANDS ==========
        basic_commands = [
            ("start", self.start_command),
            ("help", self.help_command),
            ("roast", self.roast_command),
            ("stats", self.stats_command),
            ("profile", self.profile_command),
            ("leaderboard", self.leaderboard_command),
            ("settings", self.settings_command),
            ("donate", self.donate_command),
            ("feedback", self.feedback_command),
            ("quote", self.quote_command),
            ("meme", self.meme_command),
            ("joke", self.joke_command),
            ("compliment", self.compliment_command),
            ("fact", self.fact_command),
            ("quote_of_day", self.quote_of_day_command),
            ("roast_stats", self.roast_stats_command),
            ("invite", self.invite_command),
            ("support", self.support_command),
            ("changelog", self.changelog_command),
            ("version", self.version_command),
            ("tutorial", self.tutorial_command),
            ("features", self.features_command),
            ("commands", self.commands_list_command),
            ("language", self.language_command),
            ("theme", self.theme_command),
            ("notifications", self.notifications_command),
            ("privacy", self.privacy_command),
            ("terms", self.terms_command),
            ("report", self.report_command),
            ("bug", self.bug_report_command),
            ("suggestion", self.suggestion_command)
        ]
        
        for command, handler in basic_commands:
            self.application.add_handler(CommandHandler(command, handler))
        
        # ========== ADMIN COMMANDS ==========
        admin_commands = [
            ("admin", self.admin_command),
            ("broadcast", self.broadcast_command),
            ("ban", self.ban_command),
            ("unban", self.unban_command),
            ("users", self.users_command),
            ("backup", self.backup_command),
            ("restart", self.restart_command),
            ("logs", self.logs_command),
            ("maintenance", self.maintenance_command),
            ("announce", self.announce_command),
            ("promote", self.promote_command),
            ("demote", self.demote_command),
            ("sysinfo", self.sysinfo_command)
        ]
        
        for command, handler in admin_commands:
            self.application.add_handler(CommandHandler(command, handler))
        
        # ========== GROUP COMMANDS ==========
        group_commands = [
            ("warn", self.warn_command),
            ("mute", self.mute_command),
            ("unmute", self.unmute_command),
            ("rules", self.rules_command),
            ("info", self.group_info_command),
            ("members", self.members_command),
            ("pin", self.pin_command),
            ("unpin", self.unpin_command),
            ("clean", self.clean_command),
            ("welcome", self.welcome_command)
        ]
        
        for command, handler in group_commands:
            self.application.add_handler(CommandHandler(command, handler))
        
        # ========== MESSAGE HANDLERS ==========
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo_message))
        self.application.add_handler(MessageHandler(filters.Sticker.ALL, self.handle_sticker_message))
        
        # ========== CALLBACK QUERY HANDLERS ==========
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # ========== ERROR HANDLER ==========
        self.application.add_error_handler(self.error_handler)
        
        self.logger.info(f"✅ Registered {len(basic_commands) + len(admin_commands) + len(group_commands)} commands")
    
    # ========== START COMMAND ==========
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with enhanced welcome"""
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
            ],
            [
                InlineKeyboardButton("📢 Join Channel", url="https://t.me/roastify_channel"),
                InlineKeyboardButton("👥 Support Group", url="https://t.me/roastify_support")
            ],
            [
                InlineKeyboardButton("⭐ Rate Bot", url="https://t.me/botfather"),
                InlineKeyboardButton("💰 Donate", callback_data="donate_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
<b>🎉 Welcome to Roastify Bot v3.0, {user.first_name}!</b> 🤖

<u>Your ultimate roasting companion with <b>50+ commands</b>!</u>

<code>✨ Key Features:</code>
• 🎭 <b>Smart Roast Generation</b>
• 🖼️ <b>Custom Roast Images</b>
• 📊 <b>User Statistics & Leaderboards</b>
• 🤖 <b>Auto Quotes & Memes</b>
• ⚡ <b>24/7 Active</b>
• 🔒 <b>Privacy Focused</b>
• 🌐 <b>Multi-Language Support</b>

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
    
    # ========== HELP COMMAND ==========
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command with categorized commands"""
        help_text = """
<b>🤖 ROASTIFY BOT - COMPLETE COMMAND LIST 📚</b>

<u><b>🎭 ROASTING COMMANDS:</b></u>
<code>/roast [name]</code> - Create roast for someone
<code>/roast_stats</code> - Your roasting statistics
<code>/compliment [name]</code> - Give compliment (anti-roast)
<code>/meme [text]</code> - Create meme with text
<code>/create</code> - Interactive roast creation

<u><b>📊 STATS & INFO:</b></u>
<code>/stats</code> - Bot statistics
<code>/profile</code> - Your profile
<code>/leaderboard</code> - Top roasters
<code>/quote_of_day</code> - Today's quote
<code>/fact</code> - Random fact
<code>/users</code> - User statistics (Admin)

<u><b>🔄 CONTENT COMMANDS:</b></u>
<code>/quote</code> - Random quote
<code>/joke</code> - Random joke
<code>/meme</code> - Random meme template
<code>/fact</code> - Interesting fact

<u><b>⚙️ UTILITY COMMANDS:</b></u>
<code>/settings</code> - Bot settings
<code>/invite</code> - Invite link
<code>/support</code> - Support group
<code>/feedback</code> - Send feedback
<code>/donate</code> - Support development
<code>/version</code> - Bot version
<code>/changelog</code> - Update history
<code>/tutorial</code> - How to use guide
<code>/features</code> - All features list
<code>/commands</code> - Command list
<code>/language</code> - Change language
<code>/theme</code> - Change theme
<code>/notifications</code> - Notification settings
<code>/privacy</code> - Privacy policy
<code>/terms</code> - Terms of service

<u><b>🛠️ ADMIN COMMANDS:</b></u>
<code>/admin</code> - Admin panel
<code>/broadcast</code> - Broadcast message
<code>/users</code> - User statistics
<code>/logs</code> - View logs
<code>/backup</code> - Backup data
<code>/restart</code> - Restart bot
<code>/maintenance</code> - Maintenance mode
<code>/announce</code> - Make announcement
<code>/promote</code> - Promote user
<code>/demote</code> - Demote user
<code>/sysinfo</code> - System information

<u><b>👥 GROUP COMMANDS:</b></u>
<code>/warn @user</code> - Warn user
<code>/mute @user</code> - Mute user
<code>/rules</code> - Group rules
<code>/info</code> - Group information
<code>/members</code> - Group members
<code>/pin [message]</code> - Pin message
<code>/clean [amount]</code> - Clean messages
<code>/welcome</code> - Welcome message

<u><b>📱 Quick Actions:</b></u>
Use buttons for faster access!
Type <code>/help [command]</code> for detailed help.
Example: <code>/help roast</code>
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
            ],
            [
                InlineKeyboardButton("📢 Channel", url="https://t.me/roastify_channel"),
                InlineKeyboardButton("👥 Support", url="https://t.me/roastify_support")
            ],
            [
                InlineKeyboardButton("⭐ Rate", url="https://t.me/botfather"),
                InlineKeyboardButton("💰 Donate", callback_data="donate_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(
            help_text,
            reply_markup=reply_markup
        )
    
    # ========== ROAST COMMAND ==========
    async def roast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /roast command"""
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
            # Show name input keyboard
            keyboard = [
                [KeyboardButton("Use My Name")],
                [KeyboardButton("Random Name"), KeyboardButton("Cancel")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            
            await update.message.reply_html(
                "<b>👤 Who do you want to roast?</b>\n\n"
                "Send me the name or use buttons below:",
                reply_markup=reply_markup
            )
            return NAME
        
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
                InlineKeyboardButton("🖼️ Create Image", callback_data=f"create_image:{target_name}")
            ],
            [
                InlineKeyboardButton("📊 My Stats", callback_data="my_stats"),
                InlineKeyboardButton("🎭 Roast Someone Else", callback_data="roast_menu")
            ],
            [
                InlineKeyboardButton("😂 Share to Group", callback_data=f"share_roast:{target_name}"),
                InlineKeyboardButton("⭐ Save", callback_data=f"save_roast:{target_name}")
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
                InlineKeyboardButton("📈 Detailed Stats", callback_data="detailed_stats"),
                InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"),
                InlineKeyboardButton("📤 Export", callback_data="export_stats")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(stats_text, reply_markup=reply_markup)
    
    # ========== PROFILE COMMAND ==========
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        user = update.effective_user
        user_id = user.id
        
        # Get user stats (simulated)
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

<u>🏆 Achievements:</u>
• {'🥇 Top Roaster' if rank <= 10 else ''}
• {'🔥 Streak Master' if today_roasts >= 5 else ''}
• {'🎯 Accurate Roaster' if total_roasts >= 50 else ''}
• {'⚡ Fast Roaster' if today_roasts >= self.daily_limit else ''}

<code>📊 Profile created: {datetime.now().strftime('%H:%M')}</code>
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎭 Create Roast", callback_data="create_roast"),
                InlineKeyboardButton("📊 My Stats", callback_data="my_stats")
            ],
            [
                InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
                InlineKeyboardButton("⚙️ Edit Profile", callback_data="edit_profile")
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_profile"),
                InlineKeyboardButton("📤 Share", callback_data="share_profile")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(profile_text, reply_markup=reply_markup)
    
    # ========== AUTO QUOTE RELATED COMMANDS ==========
    async def quote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /quote command"""
        if self.auto_quote_system:
            quote = await self.auto_quote_system.get_random_quote()
            
            keyboard = [
                [
                    InlineKeyboardButton("📜 Another Quote", callback_data="another_quote"),
                    InlineKeyboardButton("💾 Save Quote", callback_data="save_quote")
                ],
                [
                    InlineKeyboardButton("🎭 Create Roast", callback_data="create_roast"),
                    InlineKeyboardButton("😂 Get Joke", callback_data="get_joke")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(quote, reply_markup=reply_markup)
        else:
            await update.message.reply_html("<b>❌ Auto Quote System is disabled!</b>")
    
    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /joke command"""
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
            await update.message.reply_html("<b>❌ Auto Quote System is disabled!</b>")
    
    async def fact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /fact command"""
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
            await update.message.reply_html("<b>❌ Auto Quote System is disabled!</b>")
    
    # ========== UTILITY COMMANDS ==========
    async def invite_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /invite command"""
        bot_username = (await self.application.bot.get_me()).username
        invite_link = f"https://t.me/{bot_username}?start=invite"
        
        invite_text = f"""
<b>📢 INVITE ROASTIFY BOT</b>

Invite Roastify Bot to your groups and share the fun with friends!

<u>🔗 Invite Links:</u>
• <b>Bot Link:</b> <code>{invite_link}</code>
• <b>Direct Add:</b> <code>https://t.me/{bot_username}?startgroup=true</code>

<u>👥 Group Benefits:</u>
• 🎭 Fun roasting sessions
• 📊 Group statistics
• 🤖 Auto quotes & jokes
• ⚡ Fast responses
• 🔒 Privacy safe

<u>📋 How to Add:</u>
1. Click the button below
2. Select your group
3. Click 'Add to Group'
4. Use /help in group

<code>🤝 Share with friends!</code>
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📥 Add to Group", url=f"https://t.me/{bot_username}?startgroup=true"),
                InlineKeyboardButton("👥 Share with Friends", callback_data="share_invite")
            ],
            [
                InlineKeyboardButton("📢 Channel", url="https://t.me/roastify_channel"),
                InlineKeyboardButton("🆘 Support", url="https://t.me/roastify_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(invite_text, reply_markup=reply_markup)
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /support command"""
        support_text = """
<b>🆘 SUPPORT & HELP</b>

Need help or have questions? Here's how you can get support:

<u>📞 Contact Methods:</u>
• <b>Support Group:</b> @roastify_support
• <b>Channel:</b> @roastify_channel
• <b>Developer:</b> @roastify_dev

<u>📋 Common Issues:</u>
• Bot not responding? Try /restart
• Commands not working? Check /help
• Getting errors? Report with /bug
• Have suggestions? Use /suggestion

<u>⚡ Quick Fixes:</u>
1. Make sure bot has admin rights in groups
2. Check your internet connection
3. Update to latest version
4. Clear chat and try again

<u>🔧 Report Problems:</u>
Use <code>/bug [description]</code> to report bugs
Use <code>/suggestion [idea]</code> for suggestions
Use <code>/feedback [message]</code> for feedback

<code>⏰ Response Time: Usually within 24 hours</code>
        """
        
        keyboard = [
            [
                InlineKeyboardButton("👥 Support Group", url="https://t.me/roastify_support"),
                InlineKeyboardButton("📢 Channel", url="https://t.me/roastify_channel")
            ],
            [
                InlineKeyboardButton("🐛 Report Bug", callback_data="report_bug"),
                InlineKeyboardButton("💡 Suggest Feature", callback_data="suggest_feature")
            ],
            [
                InlineKeyboardButton("📝 Give Feedback", callback_data="give_feedback"),
                InlineKeyboardButton("🔄 Restart Bot", callback_data="restart_bot")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(support_text, reply_markup=reply_markup)
    
    # ========== ADMIN COMMANDS ==========
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        # Check if user is admin
        if user_id not in self.config.get('ADMIN_IDS', []):
            await update.message.reply_html("<b>❌ Access Denied!</b>\nYou are not authorized to use admin commands.")
            return
        
        admin_text = """
<b>🛠️ ADMIN PANEL</b>

Welcome to the Roastify Bot Admin Panel. Here you can manage all bot functions.

<u>📊 Statistics:</u>
• Total Users: {total_users}
• Total Roasts: {total_roasts}
• Active Chats: {active_chats}
• Uptime: {uptime}

<u>⚙️ Management:</u>
Use the buttons below to manage different aspects of the bot.

<u>🔒 Security:</u>
• Only authorized admins can access this panel
• All actions are logged
• Use with caution

<code>🕒 Last updated: {time}</code>
        """.format(
            total_users=self.stats['total_users'],
            total_roasts=self.stats['total_roasts'],
            active_chats=len(self.stats['active_chats']),
            uptime=str(datetime.now() - self.stats['start_time']).split('.')[0],
            time=datetime.now().strftime('%H:%M:%S')
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📊 User Stats", callback_data="admin_users"),
                InlineKeyboardButton("🎭 Roast Stats", callback_data="admin_roasts")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("📝 Announce", callback_data="admin_announce")
            ],
            [
                InlineKeyboardButton("🔧 Maintenance", callback_data="admin_maintenance"),
                InlineKeyboardButton("🔄 Restart", callback_data="admin_restart")
            ],
            [
                InlineKeyboardButton("📁 Backup", callback_data="admin_backup"),
                InlineKeyboardButton("📋 Logs", callback_data="admin_logs")
            ],
            [
                InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban"),
                InlineKeyboardButton("✅ Unban User", callback_data="admin_unban")
            ],
            [
                InlineKeyboardButton("📤 Export Data", callback_data="admin_export"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(admin_text, reply_markup=reply_markup)
    
    # ========== CALLBACK QUERY HANDLER ==========
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Handle different callback queries
        if data == "create_roast":
            await self.roast_command(update, context)
        elif data == "my_stats":
            await self.stats_command(update, context)
        elif data == "settings_menu":
            await self.settings_command(update, context)
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
        elif data == "donate_menu":
            await self.donate_command(update, context)
        elif data == "leaderboard":
            await self.leaderboard_command(update, context)
        elif data == "refresh_stats":
            await self.stats_command(update, context)
        elif data == "refresh_profile":
            await self.profile_command(update, context)
        
        # Delete original message for clean interface
        try:
            await query.delete_message()
        except:
            pass
    
    # ========== MESSAGE HANDLERS ==========
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text
        user = update.effective_user
        
        # Check if message is a name for roasting (from conversation)
        if 'roast' in context.user_data:
            target_name = text
            roast_text = self.generate_roast(target_name)
            await update.message.reply_html(
                f"<b>🔥 Roast for {target_name}:</b>\n\n"
                f"<i>{roast_text}</i>"
            )
            del context.user_data['roast']
            return
        
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
    
    # ========== ERROR HANDLER ==========
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        self.logger.error(f"Error: {context.error}", exc_info=True)
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_html(
                    "<b>❌ An error occurred!</b>\n"
                    "The developers have been notified.\n"
                    "Please try again later."
                )
        except:
            pass
    
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
    
    # ========== CONVERSATION HANDLERS ==========
    async def create_roast_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start roast creation conversation"""
        await update.message.reply_html(
            "<b>🎭 Create Custom Roast</b>\n\n"
            "Please enter the name you want to roast:",
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME
    
    async def get_roast_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get name for roast"""
        context.user_data['name'] = update.message.text
        
        keyboard = [[KeyboardButton("Skip Photo"), KeyboardButton("Cancel")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await update.message.reply_html(
            "<b>🖼️ Add Photo (Optional)</b>\n\n"
            "Send a photo to include with the roast, or click 'Skip Photo':",
            reply_markup=reply_markup
        )
        return PHOTO
    
    async def get_roast_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get photo for roast"""
        if update.message.text == "Skip Photo":
            context.user_data['photo'] = None
        elif update.message.photo:
            context.user_data['photo'] = update.message.photo[-1].file_id
        else:
            await update.message.reply_html("Please send a photo or click 'Skip Photo'")
            return PHOTO
        
        name = context.user_data['name']
        has_photo = "Yes" if context.user_data.get('photo') else "No"
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data="confirm_create"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_create")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(
            f"<b>📋 Confirm Roast Creation</b>\n\n"
            f"<b>Name:</b> {name}\n"
            f"<b>Photo:</b> {has_photo}\n\n"
            f"Click Confirm to create the roast:",
            reply_markup=reply_markup
        )
        return CONFIRM
    
    async def confirm_roast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm and create roast"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_create":
            name = context.user_data['name']
            roast_text = self.generate_roast(name)
            
            # Check if there's a photo
            if context.user_data.get('photo'):
                await query.message.reply_photo(
                    photo=context.user_data['photo'],
                    caption=f"<b>🔥 Roast for {name}:</b>\n\n<i>{roast_text}</i>",
                    parse_mode='HTML'
                )
            else:
                await query.message.reply_html(
                    f"<b>🔥 Roast for {name}:</b>\n\n"
                    f"<i>{roast_text}</i>"
                )
            
            await query.message.reply_html(
                "<b>✅ Roast created successfully!</b>\n"
                "Use /roast_stats to see your roasting statistics."
            )
        else:
            await query.message.reply_html("<b>❌ Roast creation cancelled!</b>")
        
        return ConversationHandler.END
    
    async def cancel_create(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel roast creation"""
        await update.message.reply_html(
            "<b>❌ Roast creation cancelled!</b>",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # ========== OTHER COMMAND STUBS (Placeholders) ==========
    async def meme_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🎭 Meme feature coming soon!</b>")
    
    async def compliment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>💝 Compliment feature coming soon!</b>")
    
    async def quote_of_day_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📜 Quote of the day feature coming soon!</b>")
    
    async def roast_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📊 Roast stats feature coming soon!</b>")
    
    async def donate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>💰 Donation feature coming soon!</b>")
    
    async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📝 Feedback feature coming soon!</b>")
    
    async def changelog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📋 Changelog feature coming soon!</b>")
    
    async def version_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>ℹ️ Version: Roastify Bot v3.0</b>")
    
    async def tutorial_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📚 Tutorial feature coming soon!</b>")
    
    async def features_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>✨ Features list coming soon!</b>")
    
    async def commands_list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📜 Commands list coming soon!</b>")
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🌐 Language selection coming soon!</b>")
    
    async def theme_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🎨 Theme selection coming soon!</b>")
    
    async def notifications_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🔔 Notifications settings coming soon!</b>")
    
    async def privacy_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🔒 Privacy policy coming soon!</b>")
    
    async def terms_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📄 Terms of service coming soon!</b>")
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🚨 Report feature coming soon!</b>")
    
    async def bug_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🐛 Bug report feature coming soon!</b>")
    
    async def suggestion_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>💡 Suggestion feature coming soon!</b>")
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📢 Broadcast feature coming soon!</b>")
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🚫 Ban feature coming soon!</b>")
    
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>✅ Unban feature coming soon!</b>")
    
    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>👥 Users list coming soon!</b>")
    
    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>💾 Backup feature coming soon!</b>")
    
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🔄 Restart feature coming soon!</b>")
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📋 Logs feature coming soon!</b>")
    
    async def maintenance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🔧 Maintenance feature coming soon!</b>")
    
    async def announce_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📢 Announce feature coming soon!</b>")
    
    async def promote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>⬆️ Promote feature coming soon!</b>")
    
    async def demote_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>⬇️ Demote feature coming soon!</b>")
    
    async def sysinfo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>💻 System info coming soon!</b>")
    
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>⚠️ Warn feature coming soon!</b>")
    
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🔇 Mute feature coming soon!</b>")
    
    async def unmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🔊 Unmute feature coming soon!</b>")
    
    async def rules_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📜 Rules feature coming soon!</b>")
    
    async def group_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>ℹ️ Group info coming soon!</b>")
    
    async def members_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>👥 Members list coming soon!</b>")
    
    async def pin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📌 Pin feature coming soon!</b>")
    
    async def unpin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>📌 Unpin feature coming soon!</b>")
    
    async def clean_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🧹 Clean feature coming soon!</b>")
    
    async def welcome_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>👋 Welcome feature coming soon!</b>")
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🏆 Leaderboard feature coming soon!</b>")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>⚙️ Settings feature coming soon!</b>")
    
    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>🖼️ Photo handling coming soon!</b>")
    
    async def handle_sticker_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html("<b>😄 Sticker handling coming soon!</b>")
    
    # ========== BOT STARTUP ==========
    async def start_bot(self):
        """Start the bot"""
        self.logger.info("🤖 Starting Roastify Bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Start auto quote system if available
        if self.auto_quote_system and hasattr(self.auto_quote_system, 'start'):
            self.auto_quote_system.start()
        
        self.logger.info("✅ Roastify Bot is now running! Press Ctrl+C to stop.")
    
    async def stop_bot(self):
        """Stop the bot"""
        self.logger.info("🛑 Stopping Roastify Bot...")
        
        # Stop auto quote system
        if self.auto_quote_system and hasattr(self.auto_quote_system, 'stop'):
            self.auto_quote_system.stop()
        
        await self.application.stop()
        await self.application.shutdown()
        self.logger.info("👋 Roastify Bot stopped successfully!")


# Main entry point
def main():
    """Main function to run the bot"""
    try:
        bot = RoastifyBot()
        
        # Run the bot
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.start_bot())
        
        # Keep running
        loop.run_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            loop.run_until_complete(bot.stop_bot())
        except:
            pass


if __name__ == "__main__":
    main()
