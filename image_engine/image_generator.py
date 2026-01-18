#!/usr/bin/env python3
"""
🤖 Roastify Telegram Bot - Final Fixed Version
✅ No Errors | HTML Format | Border System | Professional
"""

import os
import sys
import asyncio
import logging
import random
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from io import BytesIO

# Telegram Imports
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fix path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ==================== CONFIGURATION ====================

class Config:
    """Bot Configuration - Safe with defaults"""
    # Bot Credentials (SET THESE!)
    BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    BOT_USERNAME = os.getenv("BOT_USERNAME", "RoastifyBot")
    OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))
    
    # Image Settings
    IMAGE_WIDTH = 600
    IMAGE_HEIGHT = 450
    
    # Bot Behavior
    COOLDOWN_SECONDS = 3
    MAX_ROAST_LENGTH = 200
    MIN_ROAST_LENGTH = 2
    
    # Database
    DB_FILE = "roastify_data.json"
    
    # HTML Colors
    HTML_COLORS = {
        "primary": "#FF6B35",
        "secondary": "#00B4D8", 
        "accent": "#FFD166",
        "danger": "#EF476F",
        "success": "#06D6A0",
        "warning": "#FFD166",
        "info": "#118AB2",
        "dark": "#212529",
        "light": "#F8F9FA"
    }
    
    # Border Styles
    BORDER_STYLES = {
        "fire": {"top": "🔥", "bottom": "🔥"},
        "star": {"top": "✦", "bottom": "✦"},
        "heart": {"top": "❤️", "bottom": "❤️"},
        "diamond": {"top": "💎", "bottom": "💎"},
        "arrow": {"top": "➤", "bottom": "◀"},
        "wave": {"top": "〰️", "bottom": "〰️"},
        "music": {"top": "♪", "bottom": "♪"},
        "sparkle": {"top": "✨", "bottom": "✨"},
        "zap": {"top": "⚡", "bottom": "⚡"},
        "crown": {"top": "👑", "bottom": "👑"}
    }
    
    @staticmethod
    def validate():
        """Validate configuration"""
        if not Config.BOT_TOKEN or Config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            logger.error("❌ BOT_TOKEN not set!")
            return False
        return True

# ==================== SIMPLE DATABASE ====================

class SimpleDatabase:
    """Simple JSON database"""
    
    def __init__(self, db_file="roastify_data.json"):
        self.db_file = db_file
        self.data = self._load_data()
    
    def _load_data(self):
        """Load data from JSON"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            "users": {},
            "stats": {
                "total_roasts": 0,
                "total_users": 0,
                "start_time": datetime.now().isoformat()
            }
        }
    
    def _save_data(self):
        """Save data to JSON"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def get_user(self, user_id):
        """Get user data"""
        user_id_str = str(user_id)
        if user_id_str not in self.data["users"]:
            self.data["users"][user_id_str] = {
                "user_id": user_id,
                "roast_count": 0,
                "vote_count": 0,
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat()
            }
            self._save_data()
        return self.data["users"][user_id_str]
    
    def increment_roast(self, user_id):
        """Increment roast count"""
        user = self.get_user(user_id)
        user["roast_count"] += 1
        user["last_active"] = datetime.now().isoformat()
        self.data["stats"]["total_roasts"] += 1
        self._save_data()
        return user["roast_count"]
    
    def get_leaderboard(self, limit=10):
        """Get leaderboard"""
        users = list(self.data["users"].values())
        users.sort(key=lambda x: x["roast_count"], reverse=True)
        return users[:limit]
    
    def get_stats(self):
        """Get bot stats"""
        stats = self.data["stats"].copy()
        stats["active_users"] = len(self.data["users"])
        return stats

# ==================== SIMPLE IMAGE GENERATOR ====================

class SimpleImageGenerator:
    """Simple image generator without external dependencies"""
    
    def __init__(self):
        self.width = Config.IMAGE_WIDTH
        self.height = Config.IMAGE_HEIGHT
        self.use_pil = self._check_pil()
        logger.info(f"Image Generator: PIL = {self.use_pil}")
    
    def _check_pil(self):
        """Check if PIL is available"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            return True
        except ImportError:
            return False
    
    def create_roast_image(self, primary_text, secondary_text="", user_id=None, style="default"):
        """Create roast image"""
        try:
            if not self.use_pil:
                return self._create_text_image(primary_text, secondary_text)
            
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Create image
            img = Image.new('RGB', (self.width, self.height), (25, 25, 35))
            draw = ImageDraw.Draw(img)
            
            # Try to load font
            try:
                font_large = ImageFont.truetype("arial.ttf", 32)
                font_medium = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 18)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add top border
            draw.rectangle([(0, 0), (self.width, 10)], fill=(255, 107, 53))
            
            # Add header
            draw.text((20, 30), "🔥 Roastify Bot 🔥", font=font_large, fill=(255, 107, 53))
            
            # Add primary text
            lines = textwrap.wrap(primary_text, width=30)
            y_pos = 80
            for line in lines[:3]:
                draw.text((50, y_pos), line, font=font_medium, fill=(255, 255, 255))
                y_pos += 40
            
            # Add secondary text
            if secondary_text:
                sec_lines = textwrap.wrap(secondary_text, width=40)
                y_pos += 20
                for line in sec_lines[:2]:
                    draw.text((50, y_pos), line, font=font_medium, fill=(0, 180, 216))
                    y_pos += 30
            
            # Add bottom border
            draw.rectangle([(0, self.height-10), (self.width, self.height)], 
                          fill=(255, 107, 53))
            
            # Add footer
            if user_id:
                draw.text((20, self.height-40), f"User: {user_id}", 
                         font=font_small, fill=(150, 150, 150))
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            draw.text((self.width-100, self.height-40), timestamp, 
                     font=font_small, fill=(150, 150, 150))
            
            return img
            
        except Exception as e:
            logger.error(f"Image creation error: {e}")
            return None
    
    def _create_text_image(self, primary_text, secondary_text):
        """Create text-only image"""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (500, 300), (25, 25, 35))
            draw = ImageDraw.Draw(img)
            
            draw.text((50, 50), "ROASTIFY BOT", fill=(255, 107, 53))
            draw.text((50, 100), primary_text[:100], fill=(255, 255, 255))
            
            if secondary_text:
                draw.text((50, 150), secondary_text[:80], fill=(0, 180, 216))
            
            return img
        except:
            return None
    
    def image_to_bytes(self, image):
        """Convert image to bytes"""
        try:
            if image is None:
                return self._create_fallback_bytes()
            
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)
            return buffered
        except:
            return BytesIO()
    
    def _create_fallback_bytes(self):
        """Create fallback image bytes"""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (400, 200), (255, 107, 53))
            draw = ImageDraw.Draw(img)
            draw.text((100, 80), "🔥 Roastify Bot 🔥", fill=(255, 255, 255))
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            buffered.seek(0)
            return buffered
        except:
            return BytesIO()

# ==================== ROAST ENGINE ====================

class RoastEngine:
    """Generate roasts"""
    
    def __init__(self):
        self.roasts = self._load_roasts()
        logger.info("Roast Engine initialized")
    
    def _load_roasts(self):
        """Load roast templates"""
        return {
            "funny": [
                "তোমার বুদ্ধির দাম এক টাকা, আর ডিসকাউন্ট দুই টাকা! 🤣",
                "তুমি নিশ্চয় WiFi ছাড়া ইন্টারনেট চালাও! 😂",
                "তোমার মত ব্যক্তিত্ব দেখলে Google Maps ও হারিয়ে যায়! 🗺️",
                "তুমি যদি রেস্তোরাঁয় যাও, menu card তোমাকে পড়তে বলে! 📖",
                "তোমার স্মার্টফোনও তোমার বুদ্ধি দেখে hang হয়ে যায়! 📱"
            ],
            "savage": [
                "তোমার existence itself একটা roast! 🔥",
                "তোমাকে দেখে my wifi disconnect হয়ে যায়! 📶",
                "তুমি human error-এর definition! ⚠️",
                "তোমার মত boring person দেখলে clock ও stop হয়ে যায়! ⏰",
                "তুমি offline mode-এর advertisement! 📴"
            ],
            "general": [
                "তুমি একটু বেশিই স্পেশাল! 😎",
                "রোস্টিফাই বট সবসময় তোমার সাথে! 🤖",
                "জীবনটা ছোট, রোস্ট লং! 😈",
                "তোমার জন্য স্পেশাল রোস্ট! 😄",
                "এক্সক্লুসিভ রোস্ট শুধু তোমার জন্য! 🎯"
            ]
        }
    
    def generate_roast(self, input_text="", user_name="User"):
        """Generate a roast"""
        try:
            # Select random category
            category = random.choice(["funny", "savage", "general"])
            
            # Get random roast
            roast_text = random.choice(self.roasts[category])
            
            return {
                "primary": roast_text,
                "secondary": f"রোস্টিফাই বট | {user_name}",
                "category": category,
                "score": random.randint(1, 10)
            }
        except:
            return {
                "primary": "তোমার জন্য স্পেশাল রোস্ট! 😄",
                "secondary": "রোস্টিফাই বট",
                "category": "general",
                "score": 5
            }

# ==================== HTML MESSAGE BUILDER ====================

class HTMLMessageBuilder:
    """Build HTML messages with borders"""
    
    def __init__(self):
        self.colors = Config.HTML_COLORS
        self.border_styles = Config.BORDER_STYLES
        
        # Word variations
        self.word_variations = {
            "welcome": ["স্বাগতম", "Welcome", "হ্যালো", "Hi", "আসসালামু আলাইকুম"],
            "help": ["সাহায্য", "Help", "গাইড", "নির্দেশিকা"],
            "roast": ["রোস্ট", "Roast", "মজা", "কমেডি"],
            "stats": ["পরিসংখ্যান", "Stats", "ডাটা", "তথ্য"],
            "bot": ["বট", "Bot", "রোবট"],
            "fun": ["মজা", "Fun", "এনজয়", "আনন্দ"],
            "error": ["সমস্যা", "Error", "এরর", "বাধা"]
        }
    
    def get_random_word(self, key):
        """Get random word variation"""
        return random.choice(self.word_variations.get(key, [key]))
    
    def get_random_border(self):
        """Get random border style"""
        style = random.choice(list(self.border_styles.keys()))
        symbols = self.border_styles[style]
        return {
            "style": style,
            "top": symbols["top"] * 20,
            "bottom": symbols["bottom"] * 20
        }
    
    def create_message(self, title="", content="", footer="", add_border=True):
        """Create HTML message"""
        # Get random variations
        random_title = self.get_random_word(title.lower()) if title else ""
        random_footer = self.get_random_word(footer.lower()) if footer else ""
        
        # Build HTML
        html_parts = []
        
        if random_title:
            html_parts.append(f'<b>{random_title.upper()}</b>\n')
        
        html_parts.append(f'{content}\n')
        
        if random_footer:
            html_parts.append(f'<i>{random_footer}</i>')
        
        message = '\n'.join(html_parts)
        
        # Add border if requested
        if add_border:
            border = self.get_random_border()
            message = f"{border['top']}\n{message}\n{border['bottom']}"
        
        return message
    
    def create_command_response(self, command, user_name="", data=None):
        """Create command response"""
        responses = {
            "start": self._get_start_message(user_name),
            "help": self._get_help_message(),
            "stats": self._get_stats_message(data) if data else "স্ট্যাটস লোড হচ্ছে...",
            "roast": self._get_roast_message(),
            "ping": self._get_ping_message(),
            "leaderboard": self._get_leaderboard_message(data) if data else "লিডারবোর্ড লোড হচ্ছে...",
            "error": self._get_error_message()
        }
        
        return responses.get(command, responses["error"])
    
    def _get_start_message(self, user_name):
        """Start message"""
        return self.create_message(
            title="welcome",
            content=(
                f"👋 <b>{user_name}!</b>\n\n"
                "🤖 <i>রোস্টিফাই বটে স্বাগতম!</i>\n\n"
                "✨ <u>ব্যবহার পদ্ধতি:</u>\n"
                "• যেকোনো মেসেজ লিখুন\n"
                "• রোস্ট ইমেজ পাবেন\n"
                "• ভোট দিন রেটিং দিতে\n\n"
                "⚡ <u>কমান্ডস:</u>\n"
                "/help - সাহায্য\n"
                "/roast - রোস্ট পান\n"
                "/stats - স্ট্যাটস\n"
                "/leaderboard - লিডারবোর্ড\n\n"
                "😈 <b>মজা শুরু করি?</b>"
            ),
            footer="bot",
            add_border=True
        )
    
    def _get_help_message(self):
        """Help message"""
        return self.create_message(
            title="help",
            content=(
                "📚 <u>রোস্টিফাই বট হেল্প</u>\n\n"
                "🎯 <b>বট সম্পর্কে:</b>\n"
                "আমি একটি রোস্ট বট। আপনার মেসেজ পড়ে স্মার্ট রোস্ট তৈরি করি।\n\n"
                "⚡ <b>দ্রুত শুরু:</b>\n"
                "1. যেকোনো মেসেজ লিখুন\n"
                "2. রোস্ট ইমেজ পাবেন\n"
                "3. ভোট দিন রেটিং দিতে\n\n"
                "🛠️ <b>কমান্ড লিস্ট:</b>\n"
                "• /roast - রোস্ট পান\n"
                "• /stats - আপনার স্ট্যাটস\n"
                "• /leaderboard - টপ প্লেয়ার\n"
                "• /ping - বট চেক করুন\n"
                "• /help - এই মেসেজ\n\n"
                "🔒 <b>নিরাপত্তা:</b>\n"
                "• সবই মজার জন্য\n"
                "• কোনো অপমান নয়\n"
                "• সম্পূর্ণ বিনামূল্যে"
            ),
            footer="support",
            add_border=True
        )
    
    def _get_stats_message(self, data):
        """Stats message"""
        return self.create_message(
            title="stats",
            content=(
                f"📊 <b>পরিসংখ্যান</b>\n\n"
                f"• মোট রোস্ট: <code>{data.get('roast_count', 0)}</code>\n"
                f"• মোট ভোট: <code>{data.get('vote_count', 0)}</code>\n"
                f"• যোগদান: <code>{data.get('created_at', 'N/A')[:10]}</code>\n"
                f"• শেষ সক্রিয়: <code>{data.get('last_active', 'N/A')[:19]}</code>\n\n"
                f"🏆 র‍্যাংক: <code>#{data.get('rank', 'N/A')}</code>\n"
                f"🔥 স্ট্যাটাস: <code>সক্রিয়</code>"
            ),
            footer="updated",
            add_border=True
        )
    
    def _get_roast_message(self):
        """Roast command message"""
        return self.create_message(
            title="roast",
            content="রোস্ট তৈরি হচ্ছে... 🔥\n\nএকটু অপেক্ষা করুন!",
            footer="processing",
            add_border=True
        )
    
    def _get_ping_message(self):
        """Ping message"""
        return self.create_message(
            title="ping",
            content=(
                "🏓 <b>পং!</b>\n\n"
                "• বট স্ট্যাটাস: <code>সক্রিয় ✅</code>\n"
                "• সময়: <code>{}</code>\n"
                "• সংস্করণ: <code>3.0</code>"
            ).format(datetime.now().strftime("%H:%M:%S")),
            footer="status",
            add_border=True
        )
    
    def _get_leaderboard_message(self, data):
        """Leaderboard message"""
        if not data:
            return "লিডারবোর্ড খালি!"
        
        leaderboard_text = "🏆 <b>টপ ১০ রোস্টার</b>\n\n"
        
        for i, user in enumerate(data[:10], 1):
            name = user.get('user_id', 'Unknown')
            score = user.get('roast_count', 0)
            
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            leaderboard_text += f"{medal} User_{name} - <code>{score}</code> রোস্ট\n"
        
        leaderboard_text += f"\n📅 আপডেট: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return self.create_message(
            title="leaderboard",
            content=leaderboard_text,
            footer="competition",
            add_border=True
        )
    
    def _get_error_message(self):
        """Error message"""
        return self.create_message(
            title="error",
            content="কিছু সমস্যা হয়েছে! দয়া করে আবার চেষ্টা করুন।",
            footer="retry",
            add_border=True
        )

# ==================== MAIN BOT CLASS ====================

class RoastifyBot:
    """Main bot class - No Errors"""
    
    def __init__(self):
        """Initialize bot"""
        try:
            # Validate config
            if not Config.validate():
                logger.error("❌ Configuration validation failed!")
                return
            
            # Initialize components
            self.db = SimpleDatabase()
            self.roast_engine = RoastEngine()
            self.image_gen = SimpleImageGenerator()
            self.html_builder = HTMLMessageBuilder()
            
            # Cooldown manager
            self.cooldowns = {}
            
            # Statistics
            self.stats = {
                "start_time": datetime.now(),
                "messages": 0,
                "roasts": 0,
                "errors": 0
            }
            
            # Bot application
            self.application = None
            
            logger.info("✅ Roastify Bot initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
    
    def setup_application(self):
        """Setup Telegram application"""
        try:
            self.application = (
                ApplicationBuilder()
                .token(Config.BOT_TOKEN)
                .pool_timeout(30)
                .build()
            )
            
            # Register handlers
            self._register_handlers()
            
            logger.info("✅ Application setup completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Application setup failed: {e}")
            return False
    
    def _register_handlers(self):
        """Register all handlers"""
        # Command handlers
        commands = [
            ("start", self.handle_start),
            ("help", self.handle_help),
            ("roast", self.handle_roast),
            ("stats", self.handle_stats),
            ("leaderboard", self.handle_leaderboard),
            ("ping", self.handle_ping),
            ("info", self.handle_info),
        ]
        
        for cmd, handler in commands:
            self.application.add_handler(CommandHandler(cmd, handler))
        
        # Message handler
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_message
        ))
        
        # Error handler
        self.application.add_error_handler(self.handle_error)
        
        logger.info(f"✅ Registered {len(commands)} commands")
    
    async def set_bot_commands(self):
        """Set bot commands"""
        try:
            commands = [
                ("start", "বট শুরু করুন"),
                ("help", "সাহায্য পান"),
                ("roast", "রোস্ট পান"),
                ("stats", "আপনার স্ট্যাটস"),
                ("leaderboard", "লিডারবোর্ড দেখুন"),
                ("ping", "বট চেক করুন"),
            ]
            
            await self.application.bot.set_my_commands(commands)
            logger.info("✅ Bot commands set")
        except Exception as e:
            logger.error(f"❌ Failed to set commands: {e}")
    
    # ==================== COMMAND HANDLERS ====================
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            
            # Register user
            self.db.get_user(user.id)
            
            # Send welcome message
            welcome_msg = self.html_builder.create_command_response("start", user.first_name)
            
            # Try to send image
            try:
                image = self.image_gen.create_roast_image(
                    primary_text=f"স্বাগতম {user.first_name}!",
                    secondary_text="রোস্টিফাই বটে আপনাকে স্বাগতম",
                    user_id=user.id
                )
                
                if image:
                    image_bytes = self.image_gen.image_to_bytes(image)
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=image_bytes,
                        caption=welcome_msg,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)
            except:
                await update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)
            
            self.stats["messages"] += 1
            logger.info(f"User {user.id} started bot")
            
        except Exception as e:
            logger.error(f"Start error: {e}")
            await self._send_error(update)
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            help_msg = self.html_builder.create_command_response("help")
            await update.message.reply_text(help_msg, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            logger.error(f"Help error: {e}")
            await self._send_error(update)
    
    async def handle_roast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /roast command"""
        try:
            user = update.effective_user
            chat = update.effective_chat
            
            # Check cooldown
            if not self._check_cooldown(user.id, chat.id):
                cooldown_msg = self.html_builder.create_message(
                    title="cooldown",
                    content="⏳ দয়া করে কিছুক্ষণ অপেক্ষা করুন!",
                    footer="wait",
                    add_border=True
                )
                await update.message.reply_text(cooldown_msg, parse_mode=ParseMode.HTML)
                return
            
            # Generate roast
            roast_data = self.roast_engine.generate_roast(user_name=user.first_name)
            
            # Send typing action
            await context.bot.send_chat_action(
                chat_id=chat.id,
                action="upload_photo"
            )
            
            # Create and send image
            image = self.image_gen.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id,
                style=roast_data["category"]
            )
            
            if image:
                image_bytes = self.image_gen.image_to_bytes(image)
                
                # Send image with caption
                caption = self.html_builder.create_message(
                    title="roast",
                    content=f"🔥 {roast_data['primary']}",
                    footer=f"Score: {roast_data['score']}/10",
                    add_border=True
                )
                
                await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=image_bytes,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_to_message_id=update.message.message_id
                )
            else:
                # Fallback text
                text_msg = self.html_builder.create_message(
                    title="roast",
                    content=f"🔥 {roast_data['primary']}\n\n{roast_data['secondary']}",
                    footer="রোস্টিফাই বট",
                    add_border=True
                )
                await update.message.reply_text(text_msg, parse_mode=ParseMode.HTML)
            
            # Update database
            self.db.increment_roast(user.id)
            self.stats["roasts"] += 1
            self.stats["messages"] += 1
            
            logger.info(f"Roast sent to {user.id}")
            
        except Exception as e:
            logger.error(f"Roast error: {e}")
            await self._send_error(update)
    
    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        try:
            user = update.effective_user
            user_data = self.db.get_user(user.id)
            
            # Calculate rank
            leaderboard = self.db.get_leaderboard()
            rank = 1
            for i, u in enumerate(leaderboard, 1):
                if u["user_id"] == user.id:
                    rank = i
                    break
            
            # Add rank to data
            user_data["rank"] = rank
            
            stats_msg = self.html_builder.create_command_response("stats", data=user_data)
            await update.message.reply_text(stats_msg, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await self._send_error(update)
    
    async def handle_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /leaderboard command"""
        try:
            leaderboard = self.db.get_leaderboard(10)
            leaderboard_msg = self.html_builder.create_command_response("leaderboard", data=leaderboard)
            await update.message.reply_text(leaderboard_msg, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            logger.error(f"Leaderboard error: {e}")
            await self._send_error(update)
    
    async def handle_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ping command"""
        try:
            ping_msg = self.html_builder.create_command_response("ping")
            await update.message.reply_text(ping_msg, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            logger.error(f"Ping error: {e}")
            await self._send_error(update)
    
    async def handle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /info command"""
        try:
            uptime = datetime.now() - self.stats["start_time"]
            bot_stats = self.db.get_stats()
            
            info_text = (
                f"🤖 <b>রোস্টিফাই বট - তথ্য</b>\n\n"
                f"📊 <u>পরিসংখ্যান:</u>\n"
                f"• মোট ইউজার: <code>{bot_stats['active_users']}</code>\n"
                f"• মোট রোস্ট: <code>{bot_stats['total_roasts']}</code>\n"
                f"• আপটাইম: <code>{str(uptime).split('.')[0]}</code>\n"
                f"• এরর: <code>{self.stats['errors']}</code>\n\n"
                f"⚙️ <u>প্রযুক্তি:</u>\n"
                f"• Python Telegram Bot\n"
                f"• HTML Formatting\n"
                f"• JSON Database\n\n"
                f"👑 <u>তথ্য:</u>\n"
                f"• ওনার: <code>{Config.OWNER_ID}</code>\n"
                f"• বট: @{Config.BOT_USERNAME}\n"
                f"• সংস্করণ: 3.0"
            )
            
            info_msg = self.html_builder.create_message(
                title="info",
                content=info_text,
                footer="roastify",
                add_border=True
            )
            
            await update.message.reply_text(info_msg, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            logger.error(f"Info error: {e}")
            await self._send_error(update)
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            user = update.effective_user
            chat = update.effective_chat
            text = update.message.text
            
            self.stats["messages"] += 1
            
            # Check for very short messages
            if len(text) < Config.MIN_ROAST_LENGTH:
                return
            
            # Check cooldown
            if not self._check_cooldown(user.id, chat.id):
                return
            
            # Generate roast based on text
            roast_data = self.roast_engine.generate_roast(input_text=text, user_name=user.first_name)
            
            # Send typing action
            await context.bot.send_chat_action(
                chat_id=chat.id,
                action="upload_photo"
            )
            
            # Create and send image
            image = self.image_gen.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id,
                style=roast_data["category"]
            )
            
            if image:
                image_bytes = self.image_gen.image_to_bytes(image)
                
                caption = self.html_builder.create_message(
                    title="roast",
                    content=f"🔥 {roast_data['primary']}",
                    footer=f"{user.first_name}'র রোস্ট",
                    add_border=True
                )
                
                await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=image_bytes,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_to_message_id=update.message.message_id
                )
            else:
                # Fallback text
                text_msg = self.html_builder.create_message(
                    title="roast",
                    content=f"🔥 {roast_data['primary']}",
                    footer="রোস্টিফাই বট",
                    add_border=True
                )
                await update.message.reply_text(text_msg, parse_mode=ParseMode.HTML)
            
            # Update database
            self.db.increment_roast(user.id)
            self.stats["roasts"] += 1
            
            logger.info(f"Auto roast for {user.id}")
            
        except Exception as e:
            logger.error(f"Text message error: {e}")
            self.stats["errors"] += 1
    
    def _check_cooldown(self, user_id, chat_id):
        """Check user cooldown"""
        key = f"{user_id}_{chat_id}"
        current_time = time.time()
        
        if key in self.cooldowns:
            last_time = self.cooldowns[key]
            if current_time - last_time < Config.COOLDOWN_SECONDS:
                return False
        
        self.cooldowns[key] = current_time
        return True
    
    async def _send_error(self, update):
        """Send error message"""
        try:
            error_msg = self.html_builder.create_command_response("error")
            await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
        except:
            pass
    
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        try:
            self.stats["errors"] += 1
            
            error_msg = str(context.error)[:200]
            logger.error(f"Bot error: {error_msg}")
            
            # Notify owner
            if Config.OWNER_ID:
                try:
                    await context.bot.send_message(
                        chat_id=Config.OWNER_ID,
                        text=f"⚠️ Bot Error:\n\n<code>{error_msg}</code>",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error handler error: {e}")
    
    # ==================== BOT CONTROL ====================
    
    async def start_bot(self):
        """Start the bot"""
        try:
            logger.info("🚀 Starting Roastify Bot...")
            
            if not self.setup_application():
                raise Exception("Application setup failed")
            
            # Set commands
            await self.set_bot_commands()
            
            # Get bot info
            bot_info = await self.application.bot.get_me()
            logger.info(f"🤖 Bot Info: @{bot_info.username} (ID: {bot_info.id})")
            
            # Start
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ Bot started successfully!")
            logger.info("📡 Listening for messages...")
            
            # Keep running
            await self._keep_running()
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            await self.stop_bot()
    
    async def _keep_running(self):
        """Keep bot running"""
        try:
            while True:
                await asyncio.sleep(1)
                
                # Log status every 5 minutes
                if int(time.time()) % 300 == 0:
                    logger.info(f"📊 Status: Msgs: {self.stats['messages']} | Roasts: {self.stats['roasts']} | Errors: {self.stats['errors']}")
                    
        except asyncio.CancelledError:
            logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Keep running error: {e}")
    
    async def stop_bot(self):
        """Stop the bot"""
        try:
            logger.info("🛑 Stopping bot...")
            
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            logger.info("✅ Bot stopped")
            
        except Exception as e:
            logger.error(f"Stop error: {e}")

# ==================== MAIN FUNCTION ====================

async def main():
    """Main function"""
    try:
        print("\n" + "="*60)
        print("🤖 ROASTIFY BOT - FINAL VERSION")
        print("="*60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        # Check token
        if Config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("❌ ERROR: Please set BOT_TOKEN in environment variables!")
            print("❌ Or edit Config class in bot.py")
            return
        
        # Create and run bot
        bot = RoastifyBot()
        await bot.start_bot()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Goodbye!")
        print("="*60)

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
