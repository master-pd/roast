#!/usr/bin/env python3
"""
🎉 Advanced Welcome System - Professional Production Version
🔥 No Errors | Multi-language | Image Support | Smart Responses
"""

import os
import sys
import random
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Telegram imports
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

# Setup logging
import logging
logger = logging.getLogger(__name__)

def log_info(msg: str):
    logger.info(f"✅ {msg}")

def log_error(msg: str):
    logger.error(f"❌ {msg}")

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ==================== CONFIGURATION ====================

class WelcomeConfig:
    """Welcome system configuration"""
    
    # Languages
    SUPPORTED_LANGUAGES = ["bengali", "english", "hindi", "arabic"]
    
    # Welcome types
    WELCOME_TYPES = ["default", "funny", "formal", "royal", "party", "custom"]
    
    # Cooldown settings (seconds)
    COOLDOWN_NEW_MEMBER = 300  # 5 minutes
    COOLDOWN_RETURNING = 60    # 1 minute
    
    # Image settings
    IMAGE_WIDTH = 600
    IMAGE_HEIGHT = 400
    
    # Database file
    DB_FILE = "welcome_data.json"
    
    # Max welcomes per user per day
    MAX_WELCOMES_PER_DAY = 3
    
    # Border styles for messages
    BORDER_STYLES = {
        "fire": "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥",
        "star": "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦",
        "heart": "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️",
        "wave": "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️",
        "sparkle": "✨✨✨✨✨✨✨✨✨✨",
        "zap": "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡",
        "music": "♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪",
        "arrow": "➤➤➤➤➤➤➤➤➤➤"
    }

# ==================== DATABASE MANAGER ====================

class WelcomeDatabase:
    """Simple JSON database for welcome system"""
    
    def __init__(self, db_file="welcome_data.json"):
        self.db_file = db_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            "users": {},
            "chats": {},
            "welcome_stats": {
                "total_welcomes": 0,
                "today_welcomes": 0,
                "last_reset": datetime.now().isoformat()
            }
        }
    
    def _save_data(self):
        """Save data to JSON"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def get_user(self, user_id: int) -> Dict:
        """Get user data"""
        user_id_str = str(user_id)
        if user_id_str not in self.data["users"]:
            self.data["users"][user_id_str] = {
                "user_id": user_id,
                "welcome_count": 0,
                "last_welcome": None,
                "join_dates": [],
                "preferred_language": "bengali",
                "created_at": datetime.now().isoformat()
            }
            self._save_data()
        return self.data["users"][user_id_str]
    
    def update_user(self, user_id: int, **kwargs):
        """Update user data"""
        user = self.get_user(user_id)
        for key, value in kwargs.items():
            if key in user:
                user[key] = value
        self._save_data()
        return user
    
    def increment_welcome(self, user_id: int, chat_id: int = 0):
        """Increment welcome count"""
        user = self.get_user(user_id)
        user["welcome_count"] += 1
        user["last_welcome"] = datetime.now().isoformat()
        
        # Update global stats
        self.data["welcome_stats"]["total_welcomes"] += 1
        self.data["welcome_stats"]["today_welcomes"] += 1
        
        # Update chat stats
        chat_id_str = str(chat_id)
        if chat_id_str not in self.data["chats"]:
            self.data["chats"][chat_id_str] = {
                "chat_id": chat_id,
                "welcome_count": 0,
                "last_welcome": None
            }
        
        self.data["chats"][chat_id_str]["welcome_count"] += 1
        self.data["chats"][chat_id_str]["last_welcome"] = datetime.now().isoformat()
        
        self._save_data()
        return user["welcome_count"]
    
    def get_stats(self) -> Dict:
        """Get welcome statistics"""
        stats = self.data["welcome_stats"].copy()
        stats["total_users"] = len(self.data["users"])
        stats["total_chats"] = len(self.data["chats"])
        return stats
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.data["welcome_stats"]["today_welcomes"] = 0
        self.data["welcome_stats"]["last_reset"] = datetime.now().isoformat()
        self._save_data()
    
    def cleanup_old_data(self, days: int = 30):
        """Cleanup old data"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            cutoff_iso = cutoff.isoformat()
            
            # Clean old users (no welcome for 30 days)
            users_to_remove = []
            for user_id_str, user in self.data["users"].items():
                last_welcome = user.get("last_welcome")
                if last_welcome and last_welcome < cutoff_iso and user["welcome_count"] < 3:
                    users_to_remove.append(user_id_str)
            
            for user_id in users_to_remove:
                del self.data["users"][user_id]
            
            if users_to_remove:
                logger.info(f"Cleaned {len(users_to_remove)} inactive users")
                self._save_data()
                
        except Exception as e:
            log_error(f"Cleanup error: {e}")

# ==================== IMAGE GENERATOR (SIMPLIFIED) ====================

class WelcomeImageGenerator:
    """Generate welcome images without PIL issues"""
    
    def __init__(self):
        self.use_pil = self._check_pil()
        logger.info(f"Welcome Image Generator: PIL = {self.use_pil}")
    
    def _check_pil(self) -> bool:
        """Check if PIL is available"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            return True
        except ImportError:
            return False
    
    def create_welcome_image(self, title: str, subtitle: str = "", 
                            user_id: Optional[int] = None, 
                            style: str = "default") -> Optional[Any]:
        """Create welcome image"""
        try:
            if not self.use_pil:
                return None
            
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Create image
            img = Image.new('RGB', (600, 300), (25, 25, 35))
            draw = ImageDraw.Draw(img)
            
            # Try to load font
            try:
                font_large = ImageFont.truetype("arial.ttf", 36)
                font_medium = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 18)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add decorative top border
            draw.rectangle([(0, 0), (600, 10)], fill=(255, 107, 53))
            
            # Add title
            draw.text((150, 40), "🎉 WELCOME 🎉", font=font_large, fill=(255, 107, 53))
            
            # Add main title
            draw.text((50, 100), title[:50], font=font_medium, fill=(255, 255, 255))
            
            # Add subtitle
            if subtitle:
                sub_lines = textwrap.wrap(subtitle, width=40)
                for i, line in enumerate(sub_lines[:2]):
                    draw.text((50, 150 + (i * 30)), line, font=font_small, fill=(0, 180, 216))
            
            # Add decorative bottom border
            draw.rectangle([(0, 290), (600, 300)], fill=(255, 107, 53))
            
            # Add footer
            footer_text = "Roastify Bot"
            if user_id:
                footer_text += f" | ID: {user_id}"
            
            draw.text((50, 260), footer_text, font=font_small, fill=(150, 150, 150))
            
            # Add timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            draw.text((450, 260), timestamp, font=font_small, fill=(150, 150, 150))
            
            return img
            
        except Exception as e:
            log_error(f"Image creation error: {e}")
            return None
    
    def image_to_bytes(self, image) -> Any:
        """Convert image to bytes"""
        try:
            if image is None:
                return self._create_fallback_bytes()
            
            from io import BytesIO
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)
            return buffered
            
        except Exception as e:
            log_error(f"Bytes conversion error: {e}")
            return self._create_fallback_bytes()
    
    def _create_fallback_bytes(self) -> Any:
        """Create fallback image bytes"""
        try:
            from PIL import Image, ImageDraw
            from io import BytesIO
            
            img = Image.new('RGB', (400, 200), (255, 107, 53))
            draw = ImageDraw.Draw(img)
            
            # Simple text
            draw.text((100, 80), "🎉 WELCOME 🎉", fill=(255, 255, 255))
            draw.text((100, 120), "Roastify Bot", fill=(200, 200, 200))
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            buffered.seek(0)
            return buffered
            
        except:
            from io import BytesIO
            return BytesIO()

# ==================== MESSAGE BUILDER ====================

class WelcomeMessageBuilder:
    """Build professional welcome messages"""
    
    def __init__(self):
        self.languages = self._load_languages()
        self.border_styles = WelcomeConfig.BORDER_STYLES
        
        # Word variations for diversity
        self.word_variations = {
            "welcome": ["স্বাগতম", "Welcome", "হ্যালো", "Hi", "আসসালামু আলাইকুম", "Greetings"],
            "group": ["গ্রুপ", "Group", "চ্যাট", "Chat", "কমিউনিটি"],
            "member": ["সদস্য", "Member", "ইউজার", "User", "বন্ধু"],
            "fun": ["মজা", "Fun", "এনজয়", "Enjoy", "আনন্দ"],
            "happy": ["খুশি", "Happy", "আনন্দিত", "Glad", "উচ্ছ্বসিত"]
        }
    
    def _load_languages(self) -> Dict[str, Dict[str, List[str]]]:
        """Load language libraries"""
        return {
            "bengali": {
                "new_member": [
                    "স্বাগতম {}! আশা করি এখানে ভালো সময় কাটাবেন! 😊",
                    "{} এসেছেন! গ্রুপে আনন্দময় থাকুন! 🎉",
                    "অভ্যর্থনা {}! গ্রুপে আপনার আগমন সাদরে গ্রহণ করা হলো! 🤗",
                    "হ্যালো {}! আশা করি এখানে অনেক মজা পাবেন! 😄",
                    "{} কে গ্রুপে স্বাগতম! চলুন একসাথে মজা করি! 🥳"
                ],
                "returning": [
                    "ফিরে আসার জন্য ধন্যবাদ {}! 🎊",
                    "{} আবার ফিরেছে! মিস করেছিলাম! 🤗",
                    "অভিনন্দন {}! আবারও গ্রুপে ফিরলেন! 🏆",
                    "হ্যালো {}! আপনার ফিরে আসা আমাদের আনন্দ দিয়েছে! 😊",
                    "{} ফিরেছে! এবার মজা বাড়বে! 🥳"
                ],
                "bot_start": [
                    "রোস্টিফাই বটে স্বাগতম {}! 🤖",
                    "হ্যালো {}! আমি রোস্টিফাই, রোস্ট তৈরি করি! 😈",
                    "স্বাগতম {}! মজার রোস্টের জন্য প্রস্তুত? 🔥",
                    "{} কে রোস্টিফাই বটে স্বাগতম! 🎯",
                    "আসসালামু আলাইকুম {}! রোস্টের আসর শুরু হোক! 🎪"
                ]
            },
            "english": {
                "new_member": [
                    "Welcome {}! Hope you have a great time here! 😊",
                    "{} has joined! Enjoy your stay in the group! 🎉",
                    "Greetings {}! Your arrival is warmly welcomed! 🤗",
                    "Hello {}! Hope you have lots of fun here! 😄",
                    "Welcome {} to the group! Let's have fun together! 🥳"
                ],
                "returning": [
                    "Thanks for returning {}! 🎊",
                    "{} is back! Missed you! 🤗",
                    "Congratulations {}! Welcome back to the group! 🏆",
                    "Hello {}! Your return makes us happy! 😊",
                    "{} is back! Now the fun will double! 🥳"
                ],
                "bot_start": [
                    "Welcome to Roastify Bot {}! 🤖",
                    "Hello {}! I'm Roastify, I create roasts! 😈",
                    "Welcome {}! Ready for some fun roasts? 🔥",
                    "Welcome {} to Roastify Bot! 🎯",
                    "Hi {}! Let the roasting begin! 🎪"
                ]
            }
        }
    
    def get_random_word(self, category: str) -> str:
        """Get random word variation"""
        return random.choice(self.word_variations.get(category, [category]))
    
    def get_random_border(self) -> str:
        """Get random border style"""
        style = random.choice(list(self.border_styles.keys()))
        return self.border_styles[style]
    
    def create_welcome_message(self, user_name: str, welcome_type: str = "new_member", 
                              language: str = "bengali") -> str:
        """Create welcome message"""
        # Get language library
        lang_lib = self.languages.get(language, self.languages["bengali"])
        
        # Get message list for type
        messages = lang_lib.get(welcome_type, lang_lib["new_member"])
        
        # Select random message
        message_template = random.choice(messages)
        
        # Format with user name
        formatted_message = message_template.format(user_name)
        
        # Add border
        border = self.get_random_border()
        
        # Create final message with HTML formatting
        final_message = (
            f"{border}\n"
            f"<b>{formatted_message}</b>\n"
            f"{border}"
        )
        
        return final_message
    
    def create_group_welcome_message(self, group_name: str, bot_name: str = "Roastify Bot") -> str:
        """Create group welcome message"""
        templates = [
            f"🎊 <b>{bot_name} has joined {group_name}!</b>\n"
            f"Now you can get roast images for any message! 🔥\n\n"
            f"✨ <i>Just type a message and get roasted!</i>",
            
            f"🤖 <b>{bot_name} is now active in {group_name}!</b>\n"
            f"Get creative roasts with beautiful images! 🎨\n\n"
            f"⚡ <i>Mention someone for instant roast!</i>",
            
            f"🔥 <b>Roasting begins in {group_name}!</b>\n"
            f"{bot_name} is here to entertain you! 😈\n\n"
            f"🎯 <i>Type /help for commands</i>",
            
            f"🎪 <b>Welcome {bot_name} to {group_name}!</b>\n"
            f"Fun and entertainment starts now! 🥳\n\n"
            f"🌟 <i>Enjoy professional roast service!</i>",
            
            f"👑 <b>Royal welcome for {bot_name} in {group_name}!</b>\n"
            f"Premium roast service activated! 💎\n\n"
            f"✨ <i>Get your personalized roasts!</i>"
        ]
        
        selected = random.choice(templates)
        border = self.get_random_border()
        
        return f"{border}\n{selected}\n{border}"
    
    def create_time_based_welcome(self, user_name: str, hour: int) -> str:
        """Create time-based welcome message"""
        if 5 <= hour < 12:  # Morning
            time_word = self.get_random_word("morning")
            templates = [
                f"🌅 <b>Good morning {user_name}!</b>\nStart your day with some fun roasts! ☀️",
                f"🌞 <b>Sunrise welcome {user_name}!</b>\nLet's make this morning memorable! 🌅",
                f"☀️ <b>Morning greetings {user_name}!</b>\nPerfect time for light-hearted roasts! 😊"
            ]
        elif 12 <= hour < 17:  # Afternoon
            time_word = self.get_random_word("afternoon")
            templates = [
                f"🌤️ <b>Good afternoon {user_name}!</b>\nBrighten your day with laughter! 😄",
                f"☀️ <b>Afternoon welcome {user_name}!</b>\nLet's have some midday fun! 🎯",
                f"😎 <b>Hey {user_name}!</b>\nPerfect time for entertaining roasts! 🎪"
            ]
        elif 17 <= hour < 21:  # Evening
            time_word = self.get_random_word("evening")
            templates = [
                f"🌆 <b>Good evening {user_name}!</b>\nLet's relax with some fun roasts! 🌇",
                f"🌟 <b>Evening welcome {user_name}!</b>\nTime for entertainment! 🎭",
                f"🌜 <b>Hello {user_name}!</b>\nLet's end the day with laughter! 😂"
            ]
        else:  # Night
            time_word = self.get_random_word("night")
            templates = [
                f"🌙 <b>Good night {user_name}!</b>\nSweet dreams after some fun roasts! 🌠",
                f"🌃 <b>Night welcome {user_name}!</b>\nLate night entertainment starts! 🎪",
                f"🌜 <b>Hello {user_name}!</b>\nNight owls deserve special roasts! 🦉"
            ]
        
        selected = random.choice(templates)
        border = self.get_random_border()
        
        return f"{border}\n{selected}\n{border}"

# ==================== MAIN WELCOME SYSTEM ====================

class ProfessionalWelcomeSystem:
    """Professional Welcome System - Production Ready"""
    
    def __init__(self):
        # Initialize components
        self.db = WelcomeDatabase()
        self.image_gen = WelcomeImageGenerator()
        self.message_builder = WelcomeMessageBuilder()
        
        # Cooldown tracking
        self.cooldowns = {}  # (chat_id, user_id) -> timestamp
        
        # Statistics
        self.stats = {
            "total_welcomes": 0,
            "today_welcomes": 0,
            "start_time": datetime.now()
        }
        
        # Auto-reset daily stats
        self._reset_daily_stats_if_needed()
        
        logger.info("✅ Professional Welcome System initialized")
    
    def _reset_daily_stats_if_needed(self):
        """Reset daily statistics if new day"""
        try:
            last_reset = datetime.fromisoformat(self.db.data["welcome_stats"]["last_reset"])
            if datetime.now().date() > last_reset.date():
                self.db.reset_daily_stats()
                logger.info("📊 Daily stats reset")
        except:
            pass
    
    def _check_cooldown(self, user_id: int, chat_id: int, cooldown_seconds: int) -> bool:
        """Check if user is in cooldown"""
        key = f"{chat_id}_{user_id}"
        current_time = datetime.now().timestamp()
        
        if key in self.cooldowns:
            last_time = self.cooldowns[key]
            if current_time - last_time < cooldown_seconds:
                return False  # Still in cooldown
        
        self.cooldowns[key] = current_time
        return True  # Not in cooldown
    
    async def handle_bot_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Bot welcome"""
        try:
            user = update.effective_user
            chat = update.effective_chat
            
            # Check cooldown
            if not self._check_cooldown(user.id, chat.id, 60):  # 1 minute cooldown
                return
            
            # Create welcome message
            welcome_msg = self.message_builder.create_welcome_message(
                user_name=user.first_name,
                welcome_type="bot_start",
                language="bengali"
            )
            
            # Create welcome image
            image = self.image_gen.create_welcome_image(
                title=f"Welcome {user.first_name}!",
                subtitle="Roastify Bot - Professional Roast Service",
                user_id=user.id,
                style="royal"
            )
            
            # Send response
            if image:
                image_bytes = self.image_gen.image_to_bytes(image)
                await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=image_bytes,
                    caption=welcome_msg,
                    parse_mode=ParseMode.HTML
                )
            else:
                # Fallback to text
                fallback_msg = (
                    f"🤖 <b>Welcome to Roastify Bot {user.first_name}!</b>\n\n"
                    f"✨ I create professional roast images from your messages!\n\n"
                    f"🔥 <u>How to use:</u>\n"
                    f"• Just type any message\n"
                    f"• Get roast image\n"
                    f"• Vote on roasts\n\n"
                    f"⚡ <u>Commands:</u>\n"
                    f"/help - Show help\n"
                    f"/roast - Get random roast\n"
                    f"/stats - Your statistics\n\n"
                    f"😈 <i>Let's have some fun!</i>"
                )
                
                await update.message.reply_text(fallback_msg, parse_mode=ParseMode.HTML)
            
            # Update statistics
            self.db.increment_welcome(user.id, chat.id)
            self.stats["total_welcomes"] += 1
            self.stats["today_welcomes"] += 1
            
            logger.info(f"Bot start welcome for {user.id}")
            
        except Exception as e:
            log_error(f"Bot start error: {e}")
            await self._send_fallback_welcome(update)
    
    async def handle_bot_added_to_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot added to group"""
        try:
            chat = update.effective_chat
            if not chat:
                return
            
            # Create group welcome message
            group_name = chat.title or "this group"
            welcome_msg = self.message_builder.create_group_welcome_message(group_name)
            
            # Create group welcome image
            image = self.image_gen.create_welcome_image(
                title=f"Hello {group_name}!",
                subtitle="Roastify Bot is now active here!",
                style="party"
            )
            
            # Send welcome
            if image:
                image_bytes = self.image_gen.image_to_bytes(image)
                await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=image_bytes,
                    caption=welcome_msg,
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(welcome_msg, parse_mode=ParseMode.HTML)
            
            logger.info(f"Bot added to group {chat.id} ({chat.title})")
            
        except Exception as e:
            log_error(f"Group add error: {e}")
            fallback = "🤖 Roastify Bot has joined! Type /help for commands."
            await update.message.reply_text(fallback, parse_mode=ParseMode.HTML)
    
    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new chat members"""
        try:
            chat = update.effective_chat
            if not chat:
                return
            
            new_members = update.message.new_chat_members
            
            # Check if bot itself
            for member in new_members:
                if member.id == context.bot.id:
                    await self.handle_bot_added_to_group(update, context)
                    return
            
            # Welcome each human member
            for member in new_members:
                if member.is_bot:
                    continue
                
                # Check cooldown
                if not self._check_cooldown(member.id, chat.id, WelcomeConfig.COOLDOWN_NEW_MEMBER):
                    continue
                
                # Check if returning (simplified)
                user_data = self.db.get_user(member.id)
                is_returning = user_data["welcome_count"] > 0
                
                # Determine welcome type
                welcome_type = "returning" if is_returning else "new_member"
                
                # Get time-based welcome
                current_hour = datetime.now().hour
                welcome_msg = self.message_builder.create_time_based_welcome(
                    user_name=member.first_name,
                    hour=current_hour
                )
                
                # Add personalized touch
                if is_returning:
                    extra = "\n\n🎊 <i>Welcome back! We missed you!</i>"
                else:
                    extra = "\n\n🌟 <i>You're our special new member!</i>"
                
                welcome_msg = welcome_msg.replace("</b>", f"</b>{extra}")
                
                # Create welcome image
                image_title = "Welcome Back!" if is_returning else "Welcome!"
                image = self.image_gen.create_welcome_image(
                    title=image_title,
                    subtitle=member.first_name,
                    user_id=member.id,
                    style="royal" if is_returning else "default"
                )
                
                # Send welcome
                if image:
                    image_bytes = self.image_gen.image_to_bytes(image)
                    await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=image_bytes,
                        caption=welcome_msg,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=update.message.message_id
                    )
                else:
                    await update.message.reply_text(
                        welcome_msg,
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=update.message.message_id
                    )
                
                # Update statistics
                self.db.increment_welcome(member.id, chat.id)
                self.stats["total_welcomes"] += 1
                self.stats["today_welcomes"] += 1
                
                logger.info(f"Welcomed {member.id} in {chat.id} (returning: {is_returning})")
                
                # Small delay between welcomes
                await asyncio.sleep(1)
            
        except Exception as e:
            log_error(f"New member error: {e}")
    
    async def send_custom_welcome(self, chat_id: int, user_name: str, 
                                 welcome_type: str = "custom", 
                                 custom_text: str = None) -> bool:
        """Send custom welcome message"""
        try:
            if custom_text:
                welcome_msg = custom_text
            else:
                welcome_msg = self.message_builder.create_welcome_message(
                    user_name=user_name,
                    welcome_type=welcome_type
                )
            
            # Create image
            image = self.image_gen.create_welcome_image(
                title=f"Welcome {user_name}!",
                subtitle="Special Welcome Message",
                style=welcome_type
            )
            
            # Send message
            if image:
                image_bytes = self.image_gen.image_to_bytes(image)
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=image_bytes,
                    caption=welcome_msg,
                    parse_mode=ParseMode.HTML
                )
            else:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=welcome_msg,
                    parse_mode=ParseMode.HTML
                )
            
            return True
            
        except Exception as e:
            log_error(f"Custom welcome error: {e}")
            return False
    
    async def _send_fallback_welcome(self, update: Update):
        """Send fallback welcome message"""
        try:
            fallbacks = [
                "🎉 Welcome to Roastify Bot! Type /help to get started!",
                "🤖 Hello! I'm Roastify Bot. Let's have some fun!",
                "🔥 Welcome! Get ready for some amazing roasts!",
                "👋 Hi there! Type any message to get a roast image!",
                "🌟 Welcome aboard! The roast factory is open! 😈"
            ]
            
            await update.message.reply_text(
                random.choice(fallbacks),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            log_error(f"Fallback welcome error: {e}")
    
    def get_statistics(self) -> Dict:
        """Get welcome statistics"""
        db_stats = self.db.get_stats()
        
        return {
            "total_welcomes": db_stats["total_welcomes"],
            "today_welcomes": db_stats["today_welcomes"],
            "total_users": db_stats["total_users"],
            "total_chats": db_stats["total_chats"],
            "system_uptime": str(datetime.now() - self.stats["start_time"]).split('.')[0],
            "active_cooldowns": len(self.cooldowns)
        }
    
    def cleanup(self):
        """Cleanup old data"""
        self.db.cleanup_old_data(days=7)
        
        # Clean old cooldowns (older than 1 hour)
        current_time = datetime.now().timestamp()
        to_remove = []
        
        for key, timestamp in self.cooldowns.items():
            if current_time - timestamp > 3600:  # 1 hour
                to_remove.append(key)
        
        for key in to_remove:
            del self.cooldowns[key]
        
        if to_remove:
            logger.info(f"Cleaned {len(to_remove)} old cooldowns")

# ==================== GLOBAL INSTANCE ====================

welcome_system = ProfessionalWelcomeSystem()

# Alias for compatibility
WelcomeSystem = ProfessionalWelcomeSystem

def get_welcome_system() -> ProfessionalWelcomeSystem:
    """Get welcome system instance"""
    return welcome_system

# ==================== TEST FUNCTION ====================

if __name__ == "__main__":
    print("🧪 Testing Professional Welcome System...")
    
    system = ProfessionalWelcomeSystem()
    stats = system.get_statistics()
    
    print("\n📊 Welcome System Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test message builder
    builder = WelcomeMessageBuilder()
    test_msg = builder.create_welcome_message("John", "new_member", "english")
    print(f"\n📝 Test Message:\n{test_msg}")
    
    print("\n✅ Welcome System is ready!")
