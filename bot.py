#!/usr/bin/env python3
"""
Roastify Telegram Bot - Professional Version
হাই-কোয়ালিটি ইমেজ + টেক্সট রিপ্লাই সিস্টেম
"""

import os
import sys
import random
import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import from your project structure
try:
    from config import Config
    from utils.logger import setup_logger
    from utils.helpers import format_name, sanitize_text, generate_hash
    from utils.time_manager import TimeManager, CooldownManager
    from database.storage import DatabaseManager
    from image_engine.image_generator import ImageGenerator
    from roast_engine.roaster import RoastGenerator
    from roast_engine.safety_check import SafetyChecker
    from features.welcome_system import WelcomeSystem
    from features.mention_system import MentionSystem
    from features.admin_protection import AdminProtection
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Please check your folder structure matches the specification.")
    sys.exit(1)

from telegram import (
    Update,
    User,
    Chat,
    Message,
    ChatMember,
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputFile
)
from telegram.constants import ParseMode, ChatType, ChatAction
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ApplicationBuilder
)
from telegram.error import TelegramError, BadRequest, Forbidden

# ========== MAIN BOT CLASS ==========
class RoastifyBot:
    """Professional Roastify Bot with Image+Text replies"""
    
    def __init__(self):
        """Initialize bot with all modules"""
        # Setup logger
        self.logger = setup_logger("RoastifyBot")
        self.logger.info("🚀 Initializing Roastify Bot Professional...")
        
        # Load configuration
        self.config = Config()
        
        # Validate bot token
        if not self.config.BOT_TOKEN:
            self.logger.error("❌ BOT_TOKEN not found in config!")
            raise ValueError("Please set BOT_TOKEN in .env file")
        
        # Initialize modules
        self._init_modules()
        
        # Initialize Telegram Application
        self.application = ApplicationBuilder() \
            .token(self.config.BOT_TOKEN) \
            .concurrent_updates(True) \
            .build()
        
        # Register handlers
        self._register_handlers()
        
        # Statistics
        self.stats = {
            "total_messages": 0,
            "total_roasts": 0,
            "total_images": 0,
            "active_chats": set(),
            "start_time": datetime.now()
        }
        
        # Cooldown tracker
        self.cooldown_manager = CooldownManager(
            user_cooldown=3,
            chat_cooldown=2
        )
        
        self.logger.info("✅ Roastify Bot Professional initialized!")
        self.logger.info(f"📊 Settings: Always send both = {self.config.ALWAYS_SEND_BOTH}")
    
    def _init_modules(self):
        """Initialize all required modules"""
        try:
            # Database
            self.db = DatabaseManager()
            self.logger.info("✅ Database initialized")
            
            # Roast Generator
            self.roaster = RoastGenerator()
            self.logger.info("✅ Roast Generator initialized")
            
            # Image Generator
            self.image_gen = ImageGenerator()
            self.logger.info("✅ Image Generator initialized")
            
            # Safety Checker
            self.safety = SafetyChecker()
            self.logger.info("✅ Safety Checker initialized")
            
            # Welcome System
            self.welcome = WelcomeSystem()
            self.logger.info("✅ Welcome System initialized")
            
            # Mention System
            self.mentions = MentionSystem()
            self.logger.info("✅ Mention System initialized")
            
            # Admin Protection
            self.admin_protection = AdminProtection()
            self.logger.info("✅ Admin Protection initialized")
            
            # Time Manager
            self.time_manager = TimeManager()
            self.logger.info("✅ Time Manager initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize modules: {e}")
            raise
    
    def _register_handlers(self):
        """Register all message and command handlers"""
        
        # ========== COMMAND HANDLERS ==========
        commands = [
            ("start", self._handle_start),
            ("help", self._handle_help),
            ("roast", self._handle_roast_command),
            ("roastme", self._handle_roastme),
            ("stats", self._handle_stats),
            ("profile", self._handle_profile),
            ("leaderboard", self._handle_leaderboard),
            ("settings", self._handle_settings),
            ("invite", self._handle_invite),
            ("support", self._handle_support),
        ]
        
        for cmd, handler in commands:
            self.application.add_handler(CommandHandler(cmd, handler))
        
        # ========== MESSAGE HANDLERS ==========
        # Handle all text messages
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self._handle_text_message
            )
        )
        
        # Handle group events
        self.application.add_handler(
            MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS,
                self._handle_new_members
            )
        )
        
        # ========== CALLBACK HANDLERS ==========
        self.application.add_handler(
            CallbackQueryHandler(self._handle_callback)
        )
        
        # ========== ERROR HANDLER ==========
        self.application.add_error_handler(self._handle_error)
        
        self.logger.info(f"✅ Registered {len(commands)} commands")
    
    # ========== TEXT MESSAGE HANDLER (MAIN LOGIC) ==========
    async def _handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle ALL text messages in chats
        This is the main logic that sends IMAGE + TEXT replies
        """
        try:
            message = update.message
            if not message or not message.text:
                return
            
            user = message.from_user
            chat = message.chat
            
            # Update statistics
            self.stats["total_messages"] += 1
            self.stats["active_chats"].add(chat.id)
            
            # Log message (optional)
            if self.config.LOG_USER_MESSAGES:
                self.logger.info(f"📝 Message from {user.id} in {chat.id}: {message.text[:50]}...")
            
            # Check cooldown
            if self.cooldown_manager.is_on_cooldown(user.id, chat.id):
                return
            
            # Check message length
            if len(message.text.strip()) < self.config.MIN_MESSAGE_LENGTH:
                return
            
            # Check safety
            if not self.safety.is_safe(message.text, user.id):
                return
            
            # Check if bot should reply in this chat type
            if not self._should_reply_in_chat(chat.type):
                return
            
            # Check admin protection (don't roast admins if configured)
            if self.admin_protection.should_skip_user(user.id, chat.id):
                return
            
            # Process mentions in message
            mentioned_users = await self.mentions.extract_mentions(message)
            if mentioned_users:
                # Roast mentioned users
                for mentioned_user in mentioned_users[:3]:  # Max 3 users
                    await self._send_roast_reply(
                        target_user=mentioned_user,
                        source_user=user,
                        chat=chat,
                        original_message=message.text,
                        context=context
                    )
            else:
                # Roast the message sender
                await self._send_roast_reply(
                    target_user=user,
                    source_user=user,
                    chat=chat,
                    original_message=message.text,
                    context=context
                )
            
            # Update cooldown
            self.cooldown_manager.set_cooldown(user.id, chat.id)
            
        except Exception as e:
            self.logger.error(f"❌ Error in text message handler: {e}")
    
    async def _send_roast_reply(self, target_user: User, source_user: User, 
                               chat: Chat, original_message: str, 
                               context: ContextTypes.DEFAULT_TYPE):
        """
        Send IMAGE + TEXT roast reply
        This is the core function that sends both formats
        """
        try:
            # Generate roast text
            roast_text = self.roaster.generate_roast(
                target_name=target_user.first_name,
                original_text=original_message
            )
            
            # Generate image roast
            image_bytes = await self._generate_roast_image(
                target_user=target_user,
                source_user=source_user,
                roast_text=roast_text,
                original_message=original_message,
                chat=chat
            )
            
            # Send IMAGE reply
            if image_bytes:
                await self._send_image_reply(
                    image_bytes=image_bytes,
                    chat_id=chat.id,
                    context=context,
                    target_name=target_user.first_name
                )
                self.stats["total_images"] += 1
            
            # Send TEXT reply
            text_reply = self._format_text_reply(
                roast_text=roast_text,
                target_user=target_user,
                source_user=source_user
            )
            
            await context.bot.send_message(
                chat_id=chat.id,
                text=text_reply,
                parse_mode=ParseMode.HTML
            )
            
            # Update statistics
            self.stats["total_roasts"] += 1
            self.db.increment_roast_count(target_user.id)
            
            self.logger.info(f"🔥 Roast sent to {target_user.id} by {source_user.id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error sending roast reply: {e}")
            # Fallback: Send text only if image fails
            try:
                roast_text = self.roaster.generate_roast(
                    target_name=target_user.first_name,
                    original_text=original_message
                )
                text_reply = self._format_text_reply(
                    roast_text=roast_text,
                    target_user=target_user,
                    source_user=source_user
                )
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=text_reply,
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
    
    async def _generate_roast_image(self, target_user: User, source_user: User,
                                  roast_text: str, original_message: str,
                                  chat: Chat) -> Optional[bytes]:
        """Generate roast image using ImageGenerator"""
        try:
            # Get user profile photo
            profile_photo_bytes = None
            try:
                photos = await source_user.get_profile_photos(limit=1)
                if photos and photos.photos:
                    # Get the largest photo
                    photo = photos.photos[0][-1]
                    profile_photo_file = await photo.get_file()
                    profile_photo_bytes = await profile_photo_file.download_as_bytearray()
            except:
                profile_photo_bytes = None
            
            # Prepare data for image generation
            image_data = {
                "target_name": target_user.first_name,
                "target_username": target_user.username,
                "source_name": source_user.first_name,
                "source_username": source_user.username,
                "roast_text": roast_text,
                "original_message": original_message[:100],  # Limit length
                "chat_title": chat.title if hasattr(chat, 'title') else "",
                "timestamp": datetime.now().strftime("%H:%M"),
                "profile_photo": profile_photo_bytes
            }
            
            # Generate image
            image_bytes = await self.image_gen.generate_roast_image(image_data)
            return image_bytes
            
        except Exception as e:
            self.logger.error(f"❌ Image generation error: {e}")
            return None
    
    async def _send_image_reply(self, image_bytes: bytes, chat_id: int,
                              context: ContextTypes.DEFAULT_TYPE, target_name: str):
        """Send image reply to chat"""
        try:
            # Create InputFile from bytes
            image_file = InputFile(BytesIO(image_bytes), filename=f"roast_{target_name}.jpg")
            
            # Send image with caption
            caption = f"🔥 Roast for {target_name} \n\n<i>Generated by Roastify Pro</i>"
            
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_file,
                caption=caption,
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error sending image: {e}")
    
    def _format_text_reply(self, roast_text: str, target_user: User, 
                          source_user: User) -> str:
        """Format text reply with HTML"""
        return (
            f"<b>🔥 Roast Alert!</b>\n\n"
            f"<i>{roast_text}</i>\n\n"
            f"👤 <b>Target:</b> {target_user.first_name}\n"
            f"🎯 <b>Roasted by:</b> {source_user.first_name}\n"
            f"🕒 <b>Time:</b> {datetime.now().strftime('%I:%M %p')}\n\n"
            f"<i>Powered by Roastify Pro 🤖</i>"
        )
    
    def _should_reply_in_chat(self, chat_type: str) -> bool:
        """Check if bot should reply in this chat type"""
        if chat_type == ChatType.PRIVATE:
            return self.config.REPLY_IN_PRIVATE
        elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            return self.config.REPLY_IN_GROUPS
        elif chat_type == ChatType.CHANNEL:
            return self.config.REPLY_IN_CHANNELS
        return False
    
    # ========== COMMAND HANDLERS ==========
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            
            welcome_text = f"""
<b>🎉 Welcome to Roastify Pro, {user.first_name}!</b> 🔥

I'm an advanced Telegram bot that sends professional roast replies with images!

<b>How it works:</b>
1. I listen to all messages in chats
2. I automatically generate funny roasts
3. I send <b>HIGH-QUALITY IMAGE + TEXT</b> replies
4. I work in unlimited groups simultaneously

<b>Quick Commands:</b>
• Just chat normally - I'll reply automatically!
• <code>/roast @username</code> - Roast specific user
• <code>/roastme</code> - Roast yourself
• <code>/stats</code> - Bot statistics
• <code>/help</code> - All commands

<b>Features:</b>
✅ Professional image generation
✅ Smart mention detection  
✅ Multi-group support
✅ Safety filters
✅ Admin protection

<b>Add me to groups:</b> <code>/invite</code>

Made with ❤️ by RanaDeveloper
            """
            
            keyboard = [
                [InlineKeyboardButton("➕ Add to Group", callback_data="add_to_group")],
                [InlineKeyboardButton("📊 Bot Stats", callback_data="bot_stats")],
                [InlineKeyboardButton("🎭 Try Roast", callback_data="try_roast")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(welcome_text, reply_markup=reply_markup)
            
        except Exception as e:
            self.logger.error(f"Error in start: {e}")
    
    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
<b>🤖 ROASTIFY PRO - HELP</b>

<b>🎯 HOW TO USE:</b>
Simply add me to any group! I'll automatically reply to messages with roasts.

<b>📝 COMMANDS:</b>

<b>🎭 ROAST COMMANDS:</b>
• <code>/roast @username</code> - Roast specific user
• <code>/roastme</code> - Roast yourself
• Just mention someone in chat - I'll detect it!

<b>📊 INFO COMMANDS:</b>
• <code>/stats</code> - Bot statistics
• <code>/profile</code> - Your roast profile
• <code>/leaderboard</code> - Top roasters
• <code>/settings</code> - Bot settings

<b>🔗 UTILITY:</b>
• <code>/invite</code> - Invite link
• <code>/support</code> - Support & help

<b>⚙️ AUTO FEATURES:</b>
✅ Replies to all messages with images
✅ Detects mentions automatically
✅ Works in unlimited groups
✅ High-quality image generation

<b>📱 EXAMPLE:</b>
You: "Hey @john, you're funny!"
Bot: [Sends image roast] + [Text roast]

<b>⚠️ NOTE:</b> For entertainment only!
        """
        
        await update.message.reply_html(help_text)
    
    async def _handle_roast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /roast @username command"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "Please mention someone to roast!\n\n"
                    "Usage: <code>/roast @username</code>\n"
                    "Example: <code>/roast @john</code>",
                    parse_mode=ParseMode.HTML
                )
                return
            
            target_username = context.args[0].replace('@', '')
            source_user = update.effective_user
            
            # In a real implementation, you would:
            # 1. Lookup user by username
            # 2. Generate roast
            # 3. Send image + text
            
            roast_text = self.roaster.generate_roast(target_username, "Command roast")
            
            await update.message.reply_html(
                f"<b>🔥 Command Roast for @{target_username}:</b>\n\n"
                f"<i>{roast_text}</i>\n\n"
                f"<i>Roasted by: {source_user.first_name}</i>"
            )
            
        except Exception as e:
            self.logger.error(f"Error in roast command: {e}")
    
    async def _handle_roastme(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /roastme command"""
        try:
            user = update.effective_user
            
            # Generate self-roast
            roast_text = self.roaster.generate_roast(user.first_name, "Self roast")
            
            # Generate image
            image_data = {
                "target_name": user.first_name,
                "target_username": user.username,
                "source_name": "Yourself",
                "roast_text": roast_text,
                "original_message": "Self roast request",
                "profile_photo": None
            }
            
            image_bytes = await self.image_gen.generate_roast_image(image_data)
            
            if image_bytes:
                # Send image
                image_file = InputFile(BytesIO(image_bytes), filename=f"self_roast_{user.id}.jpg")
                await update.message.reply_photo(
                    photo=image_file,
                    caption=f"🔥 Self-roast for {user.first_name}!",
                    parse_mode=ParseMode.HTML
                )
            
            # Send text
            text_reply = (
                f"<b>😈 Self-Roast Mode Activated!</b>\n\n"
                f"<i>{roast_text}</i>\n\n"
                f"💪 <b>That takes courage, {user.first_name}!</b>"
            )
            
            await update.message.reply_html(text_reply)
            
        except Exception as e:
            self.logger.error(f"Error in roastme: {e}")
    
    async def _handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        uptime = datetime.now() - self.stats["start_time"]
        
        stats_text = f"""
<b>📊 ROASTIFY PRO STATISTICS</b>

<b>🤖 Bot Info:</b>
• Version: {self.config.VERSION}
• Uptime: {str(uptime).split('.')[0]}
• Developer: {self.config.DEVELOPER}

<b>📈 Activity Stats:</b>
• Total Messages: {self.stats['total_messages']:,}
• Total Roasts: {self.stats['total_roasts']:,}
• Total Images: {self.stats['total_images']:,}
• Active Chats: {len(self.stats['active_chats']):,}

<b>⚡ Performance:</b>
• Reply Mode: Image + Text
• Image Quality: {self.config.IMAGE_QUALITY}%
• Cooldown: {self.cooldown_manager.user_cooldown}s/user

<b>🎯 Today's Goal:</b> 10,000 roasts! 🔥
        """
        
        await update.message.reply_html(stats_text)
    
    async def _handle_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        try:
            user = update.effective_user
            user_stats = self.db.get_user_stats(user.id)
            
            profile_text = f"""
<b>👤 YOUR ROAST PROFILE</b>

<b>📝 Basic Info:</b>
• Name: {user.first_name}
• Username: @{user.username or 'N/A'}
• User ID: <code>{user.id}</code>

<b>🔥 Roast Stats:</b>
• Total Roasts Received: {user_stats.get('roasts_received', 0)}
• Total Roasts Given: {user_stats.get('roasts_given', 0)}
• Rank: #{user_stats.get('rank', 1)}
• Level: {user_stats.get('level', 1)}

<b>🏆 Achievements:</b>
• {self._get_achievement(user_stats)}

<b>📊 Activity:</b>
• First Seen: {user_stats.get('first_seen', 'Today')}
• Last Active: {user_stats.get('last_active', 'Now')}

<b>💪 Keep roasting!</b>
            """
            
            await update.message.reply_html(profile_text)
            
        except Exception as e:
            self.logger.error(f"Error in profile: {e}")
    
    def _get_achievement(self, user_stats: Dict) -> str:
        """Get user achievement"""
        roasts = user_stats.get('roasts_received', 0)
        
        if roasts >= 100:
            return "🏅 Roast Legend (100+ roasts)"
        elif roasts >= 50:
            return "🔥 Roast Master (50+ roasts)"
        elif roasts >= 25:
            return "😈 Roast Veteran (25+ roasts)"
        elif roasts >= 10:
            return "⭐ Roast Enthusiast (10+ roasts)"
        else:
            return "🌱 Roast Beginner"
    
    async def _handle_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /leaderboard command"""
        try:
            top_users = self.db.get_top_roasters(limit=10)
            
            if not top_users:
                await update.message.reply_text("No roasts yet! Start chatting to see leaderboard.")
                return
            
            leaderboard_text = "<b>🏆 TOP 10 ROASTERS</b>\n\n"
            
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            
            for idx, (user_id, username, roast_count) in enumerate(top_users):
                if idx < len(medals):
                    medal = medals[idx]
                else:
                    medal = "🏅"
                
                leaderboard_text += f"{medal} @{username or 'user'} - {roast_count} roasts\n"
            
            leaderboard_text += f"\n<b>💡 Tip:</b> Chat more to climb the ranks!"
            
            await update.message.reply_html(leaderboard_text)
            
        except Exception as e:
            self.logger.error(f"Error in leaderboard: {e}")
    
    async def _handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        settings_text = f"""
<b>⚙️ BOT SETTINGS</b>

<b>📱 Current Configuration:</b>
• Reply Mode: Image + Text
• Image Quality: {self.config.IMAGE_QUALITY}%
• Cooldown: {self.cooldown_manager.user_cooldown} seconds
• Max Message Length: {self.config.MAX_MESSAGE_LENGTH}

<b>🎨 Image Settings:</b>
• Size: {self.config.IMAGE_SIZE[0]}x{self.config.IMAGE_SIZE[1]}
• Profile Pictures: {'Enabled' if self.config.USE_PROFILE_PIC else 'Disabled'}
• Watermark: {'Enabled' if self.config.ADD_WATERMARK else 'Disabled'}

<b>🛡️ Safety Settings:</b>
• Content Filter: Active
• Spam Protection: Active
• Admin Protection: Active

<b>📊 Performance:</b>
• Active Chats: {len(self.stats['active_chats']):,}
• Messages Processed: {self.stats['total_messages']:,}
• Uptime: {str(datetime.now() - self.stats['start_time']).split('.')[0]}

<b>⚠️ Settings can only be changed by admin.</b>
        """
        
        await update.message.reply_html(settings_text)
    
    async def _handle_invite(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /invite command"""
        try:
            bot_info = await context.bot.get_me()
            bot_username = bot_info.username
            
            invite_text = f"""
<b>📢 INVITE ROASTIFY PRO</b>

<b>Add me to your groups:</b>
👉 https://t.me/{bot_username}?startgroup=true

<b>Features in groups:</b>
✅ Automatic roast replies
✅ High-quality image generation
✅ Mention detection
✅ Multi-language support
✅ Unlimited groups

<b>Why choose Roastify Pro?</b>
• Professional image design
• Fast response time
• Reliable performance
• Regular updates

<b>Share with friends:</b>
https://t.me/{bot_username}

<b>Group admin? No configuration needed!</b>
            """
            
            keyboard = [
                [InlineKeyboardButton("➕ Add to Group", 
                 url=f"https://t.me/{bot_username}?startgroup=true")],
                [InlineKeyboardButton("📱 Share Bot", 
                 url=f"https://t.me/share/url?url=https://t.me/{bot_username}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_html(invite_text, reply_markup=reply_markup)
            
        except Exception as e:
            self.logger.error(f"Error in invite: {e}")
    
    async def _handle_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /support command"""
        support_text = """
<b>🆘 SUPPORT & HELP</b>

<b>Common Issues:</b>
• Bot not replying? Check if it's added as admin
• No images? Check bot permissions
• Error messages? Try /start

<b>Bot Permissions Needed:</b>
✅ Send Messages
✅ Send Media
✅ Read Messages

<b>Contact Support:</b>
• Report bugs
• Feature requests
• General help

<b>Developer:</b> @RanaDeveloper

<b>Bot Status:</b> ✅ Online
<b>Response Time:</b> < 1 second

<b>Note:</b> This bot is for entertainment purposes only!
        """
        
        await update.message.reply_html(support_text)
    
    # ========== OTHER HANDLERS ==========
    async def _handle_new_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new members joining"""
        try:
            await self.welcome.handle_new_members(update, context)
        except Exception as e:
            self.logger.error(f"Error in new members: {e}")
    
    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            
            if data == "add_to_group":
                bot_info = await context.bot.get_me()
                await query.message.reply_text(
                    f"Add me to group:\n\n"
                    f"https://t.me/{bot_info.username}?startgroup=true"
                )
            
            elif data == "bot_stats":
                await self._handle_stats(update, context)
            
            elif data == "try_roast":
                user = update.effective_user
                roast_text = self.roaster.generate_roast(user.first_name, "Demo roast")
                await query.message.reply_html(
                    f"<b>Demo Roast:</b>\n\n"
                    f"<i>{roast_text}</i>"
                )
            
        except Exception as e:
            self.logger.error(f"Error in callback: {e}")
    
    async def _handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        try:
            error = context.error
            self.logger.error(f"Bot error: {error}", exc_info=True)
        except:
            pass
    
    # ========== BOT CONTROL ==========
    async def start(self):
        """Start the bot"""
        self.logger.info("🤖 Starting Roastify Bot Pro...")
        
        try:
            # Create necessary directories
            for directory in ['logs', 'generated', 'temp', 'data']:
                Path(directory).mkdir(exist_ok=True)
            
            # Start bot
            await self.application.initialize()
            await self.application.start()
            
            # Get bot info
            bot_info = await self.application.bot.get_me()
            self.config.BOT_USERNAME = bot_info.username
            
            self.logger.info(f"✅ Bot started as @{bot_info.username}")
            print("\n" + "="*50)
            print("🎉 ROASTIFY BOT PRO - STARTED SUCCESSFULLY!")
            print("="*50)
            print(f"🤖 Username: @{bot_info.username}")
            print(f"🚀 Version: {self.config.VERSION}")
            print(f"📊 Mode: IMAGE + TEXT replies")
            print(f"👥 Supports: Unlimited groups")
            print(f"🛑 Press Ctrl+C to stop")
            print("="*50 + "\n")
            
            # Start polling
            await self.application.updater.start_polling()
            
            # Keep running
            await asyncio.Event().wait()
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Bot stopped by user")
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Failed to start bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot"""
        self.logger.info("🛑 Stopping bot...")
        
        try:
            if hasattr(self, 'application') and self.application.running:
                await self.application.stop()
                await self.application.shutdown()
            
            self.logger.info("👋 Bot stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping bot: {e}")
    
    def run(self):
        """Run the bot (blocking)"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            print(f"\n❌ Fatal error: {e}")


# ========== MAIN ENTRY POINT ==========
if __name__ == "__main__":
    try:
        bot = RoastifyBot()
        bot.run()
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)
