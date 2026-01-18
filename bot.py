#!/usr/bin/env python3
"""
Roastify Telegram Bot - Advanced HTML Version
Random Borders | Random Styles | Professional
"""

import os
import sys
import asyncio
import traceback
import random
from typing import Dict, List, Optional, Any
from telegram import Update, BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
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

# Fix encoding for Termux
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except:
    pass

# Import configurations and modules
from config import Config
from utils.logger import logger, log_error, log_info
from utils.time_manager import TimeManager
from utils.helpers import Helpers
from utils.text_processor import TextProcessor
from database.storage import StorageManager
from database.models import init_database, User
from roast_engine.roaster import RoastEngine
from roast_engine.safety_check import safety_checker
from image_engine.image_generator import get_image_generator
from features.welcome_system import WelcomeSystem
from features.vote_system import VoteSystem
from features.mention_system import MentionSystem
from features.reaction_system import ReactionSystem
from features.admin_protection import AdminProtection
from features.auto_quotes import AutoQuoteSystem

class RoastifyBot:
    """রোস্টিফাই বট - Advanced HTML Version"""
    
    def __init__(self):
        """বট ইনিশিয়ালাইজেশন"""
        try:
            # Validate configuration
            Config.validate()
            
            # Initialize components
            self.roast_engine = RoastEngine()
            self.text_processor = TextProcessor()
            self.welcome_system = WelcomeSystem()
            self.vote_system = VoteSystem()
            self.mention_system = MentionSystem()
            self.reaction_system = ReactionSystem()
            self.admin_protection = AdminProtection()
            self.auto_quotes = AutoQuoteSystem()
            
            # Initialize database
            init_database()
            
            # Image generator
            self.image_generator = get_image_generator()
            
            # Bot state
            self.application = None
            self.is_running = False
            self.user_cooldowns = {}
            self.chat_stats = {}
            
            # Performance tracking
            self.stats = {
                'total_messages': 0,
                'total_roasts': 0,
                'total_votes': 0,
                'total_errors': 0,
                'start_time': TimeManager.get_current_time()
            }
            
            # Random border styles
            self.border_styles = {
                "fire": {"top": "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥", "bottom": "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥"},
                "star": {"top": "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦", "bottom": "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦"},
                "heart": {"top": "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️", "bottom": "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️"},
                "diamond": {"top": "💎💎💎💎💎💎💎💎💎💎", "bottom": "💎💎💎💎💎💎💎💎💎💎"},
                "arrow": {"top": "➤➤➤➤➤➤➤➤➤➤", "bottom": "◀◀◀◀◀◀◀◀◀◀"},
                "wave": {"top": "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️", "bottom": "〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️"},
                "music": {"top": "♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪", "bottom": "♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪♪"},
                "sparkle": {"top": "✨✨✨✨✨✨✨✨✨✨", "bottom": "✨✨✨✨✨✨✨✨✨✨"},
                "double_line": {"top": "════════════════════", "bottom": "════════════════════"},
                "bold_line": {"top": "━━━━━━━━━━━━━━━━━━━━", "bottom": "━━━━━━━━━━━━━━━━━━━━"},
                "dotted": {"top": "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈", "bottom": "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈"},
                "zap": {"top": "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡", "bottom": "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡"},
                "crown": {"top": "👑👑👑👑👑👑👑👑👑👑", "bottom": "👑👑👑👑👑👑👑👑👑👑"},
                "smile": {"top": "😊😊😊😊😊😊😊😊😊😊", "bottom": "😊😊😊😊😊😊😊😊😊😊"},
                "ghost": {"top": "👻👻👻👻👻👻👻👻👻👻", "bottom": "👻👻👻👻👻👻👻👻👻👻"},
                "rocket": {"top": "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀", "bottom": "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀"},
            }
            
            # Random text styles
            self.text_styles = [
                # Style 1: Simple with emoji
                lambda text, title: f'<b>{title}</b>\n\n{text}\n\n<i>🔥 Roastify Bot 🔥</i>',
                
                # Style 2: Centered
                lambda text, title: f'<center><b>{title}</b></center>\n\n{text}\n\n<center><i>✨ Professional Roast Service ✨</i></center>',
                
                # Style 3: With header line
                lambda text, title: f'<u><b>{title}</b></u>\n\n{text}\n\n<code>─────────────</code>',
                
                # Style 4: Quote style
                lambda text, title: f'❝ {text} ❞\n\n— <i>{title}</i>',
                
                # Style 5: Box style
                lambda text, title: f'▌ <b>{title}</b> ▌\n\n{text}\n\n▌ <i>Roastify Bot</i> ▌',
                
                # Style 6: Simple bold
                lambda text, title: f'<b>{title}</b>\n{text}',
                
                # Style 7: With timestamp
                lambda text, title: f'🕒 <b>{TimeManager.get_current_time().strftime("%H:%M")}</b>\n\n<b>{title}</b>\n{text}',
                
                # Style 8: Emoji decorated
                lambda text, title: f'🎯 <b>{title}</b> 🎯\n\n✨ {text} ✨',
                
                # Style 9: Code style
                lambda text, title: f'<code>┌─[ {title} ]─┐</code>\n{text}\n<code>└───────────────┘</code>',
                
                # Style 10: Modern
                lambda text, title: f'<b>┏━━ {title} ━━┓</b>\n\n{text}\n\n<b>┗━━ Roastify ━━┛</b>',
            ]
            
            # Random word variations
            self.word_variations = {
                "welcome": ["স্বাগতম", "আসসালামু আলাইকুম", "Welcome", "হ্যালো", "Hi there"],
                "help": ["সাহায্য", "হেল্প", "গাইড", "নির্দেশিকা"],
                "bot": ["বট", "Bot", "Robot", "স্বয়ংক্রিয়"],
                "roast": ["রোস্ট", "মজা", "জোক", "কমেডি"],
                "funny": ["মজার", "হাসির", "কৌতুক", "এন্টারটেইনমেন্ট"],
                "savage": ["স্যাভেজ", "তীব্র", "কঠোর", "বেপরোয়া"],
                "enjoy": ["উপভোগ করুন", "এনজয়", "মজা নিন", "আনন্দ নিন"],
                "thanks": ["ধন্যবাদ", "Thank you", "শুকরিয়া", "মোবারক"],
            }
            
            logger.info("✅ RoastifyBot Advanced HTML Version initialized")
            logger.info(f"🤖 Bot: @{Config.BOT_USERNAME}")
            logger.info(f"👑 Owner: {Config.OWNER_ID}")
            
        except Exception as e:
            log_error(f"Failed to initialize bot: {e}")
            raise
    
    # ==================== RANDOM HTML HELPER METHODS ====================
    
    def _get_random_border(self) -> Dict[str, str]:
        """Get random border style"""
        style_name = random.choice(list(self.border_styles.keys()))
        return {
            "name": style_name,
            "top": self.border_styles[style_name]["top"],
            "bottom": self.border_styles[style_name]["bottom"]
        }
    
    def _get_random_style(self):
        """Get random text style function"""
        return random.choice(self.text_styles)
    
    def _get_random_word(self, key: str) -> str:
        """Get random word variation"""
        if key in self.word_variations:
            return random.choice(self.word_variations[key])
        return key
    
    def _wrap_with_random_border(self, content: str) -> str:
        """Add random border to message"""
        border = self._get_random_border()
        return f"{border['top']}\n{content}\n{border['bottom']}"
    
    def _format_random_html_message(self, title: str = "", content: str = "", 
                                  footer: str = "", add_border: bool = True) -> str:
        """Format message with random HTML style and border"""
        
        # Get random variations
        random_title = self._get_random_word(title.lower()) if title else ""
        random_footer = self._get_random_word(footer.lower()) if footer else footer
        
        # Get random style function
        style_func = self._get_random_style()
        
        # Apply style
        if title:
            styled_content = style_func(content, random_title.title())
        else:
            styled_content = style_func(content, "")
        
        # Add footer if exists
        if random_footer:
            styled_content += f"\n\n<i>{random_footer}</i>"
        
        # Add random border
        if add_border:
            final_message = self._wrap_with_random_border(styled_content)
        else:
            final_message = styled_content
        
        return final_message
    
    # ==================== COMMAND HANDLERS - RANDOM HTML VERSION ====================
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start কমান্ড - Random HTML"""
        try:
            user = update.effective_user
            chat = update.effective_chat
            
            # Track user
            StorageManager.get_or_create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            # Random welcome variations
            welcome_variations = [
                f"হ্যালো {user.first_name}! আমি রোস্টিফাই বট",
                f"Welcome {user.first_name}! Let's have some fun",
                f"আসসালামু আলাইকুম {user.first_name}! রোস্টের জন্য তৈরি?",
                f"Hi {user.first_name}! Ready for some savage roasts?",
                f"স্বাগতম {user.first_name}! মজা শুরু করি?"
            ]
            
            help_variations = [
                "শুধু মেসেজ লিখুন → রোস্ট পাবেন",
                "Just type a message → Get roasted",
                "গ্রুপে মেনশন করুন → ইন্সট্যান্ট রোস্ট",
                "Use /roast for instant roast",
                "ভোট দিয়ে রেটিং দিন → লিডারবোর্ডে উঠুন"
            ]
            
            # Create random HTML message
            welcome_html = self._format_random_html_message(
                title=random.choice(["welcome", "hello", "hi", "greetings"]),
                content=(
                    f"{random.choice(welcome_variations)}! 😈\n\n"
                    f"<u>📋 {self._get_random_word('usage')}:</u>\n"
                    f"• {random.choice(help_variations)}\n"
                    f"• {random.choice(help_variations)}\n"
                    f"• {random.choice(help_variations)}\n\n"
                    
                    f"<u>🛠️ {self._get_random_word('commands')}:</u>\n"
                    f"/help - {self._get_random_word('help')}\n"
                    f"/stats - {self._get_random_word('stats')}\n"
                    f"/roast - {self._get_random_word('roast')}\n"
                    f"/quote - {self._get_random_word('quote')}\n\n"
                    
                    f"<b>🔥 {self._get_random_word('ready')}? {self._get_random_word('start')}!</b>"
                ),
                footer=f"{self._get_random_word('bot')}: @{Config.BOT_USERNAME}",
                add_border=True
            )
            
            # Create welcome image
            try:
                image = self.image_generator.create_roast_image(
                    primary_text=f"{self._get_random_word('welcome')} {user.first_name}!",
                    secondary_text=f"{self._get_random_word('ready')} {self._get_random_word('roast')}? 😈",
                    user_id=user.id
                )
                
                image_path = self.image_generator.save_image(image)
                
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=photo,
                        caption=welcome_html,
                        parse_mode=ParseMode.HTML
                    )
                    
            except Exception as e:
                logger.warning(f"Could not send welcome image: {e}")
                await update.message.reply_text(welcome_html, parse_mode=ParseMode.HTML)
            
            self.stats['total_messages'] += 1
            logger.info(f"User {user.id} started the bot")
            
        except Exception as e:
            log_error(f"Error in handle_start: {e}")
            await self._send_error_message(update, "start")
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/help কমান্ড - Random HTML"""
        try:
            # Random help content variations
            about_variations = [
                "আমি একটি এডভান্সড রোস্ট বট",
                "I'm an advanced roast bot",
                "স্মার্ট রোস্ট জেনারেশন",
                "AI-powered roast generation",
                "প্রফেশনাল কমেডি সার্ভিস"
            ]
            
            feature_variations = [
                "ইমেজ সহ রোস্ট",
                "ভোট সিস্টেম",
                "লিডারবোর্ড",
                "র‍্যান্ডম রোস্ট",
                "গ্রুপ সাপোর্ট"
            ]
            
            command_variations = [
                "/roast - ইন্সট্যান্ট রোস্ট",
                "/stats - পার্সোনাল স্ট্যাটস", 
                "/leaderboard - টপ প্লেয়ার",
                "/quote - ইনস্পিরেশনাল কোট",
                "/ping - বট চেক"
            ]
            
            # Random HTML message
            help_html = self._format_random_html_message(
                title=random.choice(["help", "guide", "manual", "instructions"]),
                content=(
                    f"<u>🎯 {self._get_random_word('about')}:</u>\n"
                    f"<i>{random.choice(about_variations)}। আপনার মেসেজের উপর ভিত্তি করে "
                    f"স্মার্ট রোস্ট তৈরি করি।</i>\n\n"
                    
                    f"<u>✨ {self._get_random_word('features')}:</u>\n"
                    f"• {random.choice(feature_variations)}\n"
                    f"• {random.choice(feature_variations)}\n"
                    f"• {random.choice(feature_variations)}\n"
                    f"• {random.choice(feature_variations)}\n\n"
                    
                    f"<u>⚡ {self._get_random_word('quick')} {self._get_random_word('commands')}:</u>\n"
                    f"{random.choice(command_variations)}\n"
                    f"{random.choice(command_variations)}\n"
                    f"{random.choice(command_variations)}\n"
                    f"{random.choice(command_variations)}\n\n"
                    
                    f"<u>🔒 {self._get_random_word('safety')}:</u>\n"
                    f"• {self._get_random_word('no')} {self._get_random_word('offensive')} {self._get_random_word('content')}\n"
                    f"• {self._get_random_word('all')} {self._get_random_word('fun')}!\n"
                    f"• {self._get_random_word('respectful')} {self._get_random_word('roasts')}"
                ),
                footer=f"🤖 {self._get_random_word('support')}: /start",
                add_border=True
            )
            
            await update.message.reply_text(help_html, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            log_error(f"Error in handle_help: {e}")
            await self._send_error_message(update, "help")
    
    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/stats কমান্ড - Random HTML"""
        try:
            user = update.effective_user
            
            # Get user stats from database
            with StorageManager.get_session() as db:
                user_record = db.query(User).filter(User.user_id == user.id).first()
                
                if user_record:
                    # Random stat variations
                    stat_variations = [
                        f"📊 {user.first_name}'র {self._get_random_word('stats')}",
                        f"📈 {self._get_random_word('performance')} {self._get_random_word('report')}",
                        f"🎯 {user.first_name}'র {self._get_random_word('analytics')}",
                        f"📋 {self._get_random_word('user')} {self._get_random_word('stats')}",
                        f"🔍 {self._get_random_word('insights')} {self._get_random_word('for')} {user.first_name}"
                    ]
                    
                    rank_variations = [
                        "র‍্যাংক",
                        "পজিশন", 
                        "স্ট্যান্ডিং",
                        "প্লেস",
                        "অর্ডার"
                    ]
                    
                    status_variations = [
                        "সক্রিয়",
                        "অ্যাক্টিভ",
                        "এনগেজড",
                        "পার্টিসিপেটিং",
                        "জয়েনড"
                    ]
                    
                    stats_html = self._format_random_html_message(
                        title=random.choice(stat_variations),
                        content=(
                            f"• {self._get_random_word('total')} {self._get_random_word('roasts')}: <code>{user_record.roast_count}</code>\n"
                            f"• {self._get_random_word('total')} {self._get_random_word('votes')}: <code>{user_record.vote_count}</code>\n"
                            f"• {self._get_random_word('reactions')}: <code>{user_record.reaction_count}</code>\n"
                            f"• {self._get_random_word('joined')}: <code>{TimeManager.format_time(user_record.created_at)}</code>\n\n"
                            
                            f"🏆 {random.choice(rank_variations)}: <code>#{self._get_user_rank(user.id)}</code>\n"
                            f"🔥 {self._get_random_word('activity')}: <code>{random.choice(status_variations)}</code>"
                        ),
                        footer=f"📅 {self._get_random_word('updated')}: {TimeManager.format_time()}",
                        add_border=True
                    )
                else:
                    stats_html = self._format_random_html_message(
                        title=random.choice(["stats", "analytics", "data"]),
                        content=(
                            f"📊 {self._get_random_word('stats')} {self._get_random_word('not')} {self._get_random_word('found')}!\n\n"
                            f"{self._get_random_word('you')} {self._get_random_word('havent')} {self._get_random_word('received')} {self._get_random_word('any')} {self._get_random_word('roasts')} {self._get_random_word('yet')}!\n"
                            f"{self._get_random_word('send')} {self._get_random_word('a')} {self._get_random_word('message')} {self._get_random_word('to')} {self._get_random_word('get')} {self._get_random_word('started')}."
                        ),
                        footer=f"🚀 {self._get_random_word('start')}: /roast",
                        add_border=True
                    )
            
            await update.message.reply_text(stats_html, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            log_error(f"Error in handle_stats: {e}")
            await self._send_error_message(update, "stats")
    
    # ==================== TEXT MESSAGE HANDLER - RANDOM RESPONSES ====================
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """টেক্সট মেসেজ হ্যান্ডল করে - Random Responses"""
        try:
            message = update.effective_message
            user = update.effective_user
            chat = update.effective_chat
            
            self.stats['total_messages'] += 1
            
            # Check admin protection
            if await self.admin_protection.check_and_protect(update, context):
                return
            
            # Check for mentions
            if await self.mention_system.handle_mention(update, context):
                return
            
            # Validate input
            if not self._validate_user_input(message.text, user.id, chat.id):
                # Send random cooldown message
                cooldown_messages = [
                    f"⏳ {self._get_random_word('please')} {self._get_random_word('wait')}!",
                    f"🔥 {self._get_random_word('too')} {self._get_random_word('fast')}!",
                    f"⚡ {self._get_random_word('slow')} {self._get_random_word('down')}!",
                    f"🎯 {self._get_random_word('cooldown')} {self._get_random_word('active')}",
                    f"⏱️ {self._get_random_word('wait')} {self._get_random_word('a')} {self._get_random_word('bit')}"
                ]
                
                await update.message.reply_text(
                    random.choice(cooldown_messages),
                    parse_mode=ParseMode.HTML
                )
                return
            
            # Generate roast with random variations
            roast_data = self.roast_engine.generate_roast(message.text, user.id)
            
            # Random roast category names
            category_names = {
                "general": ["সাধারণ", "জেনারেল", "বেসিক", "স্ট্যান্ডার্ড"],
                "funny": ["মজার", "হাসির", "কমেডি", "এন্টারটেইনমেন্ট"],
                "savage": ["স্যাভেজ", "কঠোর", "তীব্র", "বেপরোয়া"],
                "creative": ["ক্রিয়েটিভ", "সৃজনশীল", "ইনোভেটিভ", "ইউনিক"]
            }
            
            category = roast_data.get("category", "general")
            random_category = random.choice(category_names.get(category, ["রোস্ট"]))
            
            # Send typing action
            await context.bot.send_chat_action(
                chat_id=chat.id,
                action="upload_photo"
            )
            
            # Random image styles
            image_styles = ["default", "funny", "savage", "welcome", "vibrant"]
            random_style = random.choice(image_styles)
            
            # Create and send image with random variations
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id,
                roast_type=random_style
            )
            
            if image:
                image_path = self.image_generator.save_image(image)
                
                # Random captions
                captions = [
                    f"🔥 {self._get_random_word('here')} {self._get_random_word('is')} {self._get_random_word('your')} {self._get_random_word('roast')}!",
                    f"🎯 {self._get_random_word('roast')} {self._get_random_word('delivered')}!",
                    f"⚡ {self._get_random_word('fresh')} {self._get_random_word('roast')} {self._get_random_word('for')} {user.first_name}!",
                    f"😈 {self._get_random_word('enjoy')} {self._get_random_word('this')} {self._get_random_word('one')}!",
                    f"💀 {self._get_random_word('savage')} {self._get_random_word('mode')} {self._get_random_word('activated')}!"
                ]
                
                with open(image_path, 'rb') as photo:
                    sent_message = await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=photo,
                        caption=random.choice(captions),
                        reply_to_message_id=message.message_id,
                        parse_mode=ParseMode.HTML
                    )
                
                # Add vote buttons with random text
                await self.vote_system.add_vote_to_message(
                    update, context, sent_message.message_id, chat.id
                )
                
                self.stats['images_sent'] += 1
            else:
                # Fallback text response with random variation
                fallback_responses = [
                    f"🔥 *{random_category} রোস্ট!*\n\n{roast_data['primary']}\n\n{roast_data['secondary']}",
                    f"🎯 {self._get_random_word('roast')} {self._get_random_word('time')}!\n\n{roast_data['primary']}",
                    f"⚡ {user.first_name}'র {self._get_random_word('roast')}:\n\n{roast_data['primary']}",
                    f"😈 {self._get_random_word('here')} {self._get_random_word('we')} {self._get_random_word('go')}:\n\n{roast_data['primary']}"
                ]
                
                await update.message.reply_text(
                    random.choice(fallback_responses),
                    parse_mode=ParseMode.HTML
                )
            
            # Update database
            StorageManager.get_or_create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            StorageManager.log_roast(
                user_id=user.id,
                input_text=message.text[:200],
                roast_type=roast_data["category"],
                template_used=random_style,
                chat_id=chat.id
            )
            
            StorageManager.increment_user_roast_count(user.id)
            
            # Add random auto-reactions
            await self.reaction_system.analyze_and_react(update, context)
            
            self.stats['total_roasts'] += 1
            
            logger.info(f"Roasted user {user.id} in chat {chat.id} with style: {random_style}")
            
        except Exception as e:
            self.stats['total_errors'] += 1
            log_error(f"Error in handle_text_message: {e}")
            
            # Random error messages
            error_variations = [
                f"😓 {self._get_random_word('roast')} {self._get_random_word('generation')} {self._get_random_word('failed')}! {self._get_random_word('try')} {self._get_random_word('again')}.",
                f"⚡ {self._get_random_word('brain')} {self._get_random_word('overload')}! {self._get_random_word('restarting')}...",
                f"🎯 {self._get_random_word('oops')}! {self._get_random_word('something')} {self._get_random_word('went')} {self._get_random_word('wrong')}.",
                f"🔥 {self._get_random_word('technical')} {self._get_random_word('difficulty')}! {self._get_random_word('please')} {self._get_random_word('wait')}.",
                f"🤖 {self._get_random_word('system')} {self._get_random_word('error')}! {self._get_random_word('recovering')}..."
            ]
            
            await update.message.reply_text(
                random.choice(error_variations),
                parse_mode=ParseMode.HTML
            )
    
    # ==================== OTHER HANDLERS WITH RANDOMIZATION ====================
    
    async def handle_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/ping কমান্ড - Random Response"""
        try:
            start_time = TimeManager.get_current_time()
            
            # Random ping messages
            ping_messages = [
                "🏓 পিং...",
                "⚡ চেকিং...",
                "🎯 টেস্টিং...",
                "🤖 কানেকশন...",
                "🔥 লেটেন্সি..."
            ]
            
            pong_messages = [
                "🏓 পং!",
                "⚡ কানেক্টেড!",
                "🎯 রেসপন্স!",
                "🤖 অ্যাকটিভ!",
                "🔥 লাইভ!"
            ]
            
            ping_message = await update.message.reply_text(
                random.choice(ping_messages),
                parse_mode=ParseMode.HTML
            )
            
            end_time = TimeManager.get_current_time()
            latency = (end_time - start_time).total_seconds() * 1000
            
            # Random response format
            response_formats = [
                f"{random.choice(pong_messages)}\n\n• {self._get_random_word('latency')}: <code>{latency:.0f}ms</code>\n• {self._get_random_word('status')}: <code>অ্যাকটিভ ✅</code>\n• {self._get_random_word('time')}: <code>{TimeManager.format_time()}</code>",
                f"⚡ <b>পারফরম্যান্স রিপোর্ট</b>\n\n📊 {self._get_random_word('latency')}: <code>{latency:.0f}ms</code>\n✅ {self._get_random_word('status')}: <code>স্টেবল</code>\n🕒 {self._get_random_word('time')}: <code>{TimeManager.format_time()}</code>",
                f"🎯 <b>সিস্টেম চেক</b>\n\n⚡ {self._get_random_word('response')}: <code>{latency:.0f}ms</code>\n🤖 {self._get_random_word('bot')}: <code>অপারেশনাল</code>\n📅 {self._get_random_word('timestamp')}: <code>{TimeManager.format_time()}</code>"
            ]
            
            await ping_message.edit_text(
                random.choice(response_formats),
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            log_error(f"Error in handle_ping: {e}")
            await self._send_error_message(update, "ping")
    
    async def _send_error_message(self, update: Update, command: str):
        """এরর মেসেজ পাঠায় - Random Error Messages"""
        try:
            error_variations = {
                'start': [
                    "😓 বট শুরু করতে সমস্যা! আবার চেষ্টা করুন।",
                    "⚡ স্টার্ট ফেইলড! প্লিজ রিট্রাই।",
                    "🎯 ইনিশিয়ালাইজেশন এরর! /start দিন আবার।"
                ],
                'help': [
                    "🤖 হেল্প লোড করতে সমস্যা!",
                    "📚 গাইড এক্সেস এরর!",
                    "⚡ হেল্প সিস্টেম ফেইলড!"
                ],
                'stats': [
                    "📊 স্ট্যাটস দেখাতে সমস্যা!",
                    "📈 ডাটা লোড এরর!",
                    "🎯 অ্যানালিটিক্স ফেইলড!"
                ],
                'roast': [
                    "🔥 রোস্ট তৈরি করতে সমস্যা!",
                    "😈 রোস্ট জেনারেশন ফেইলড!",
                    "⚡ কমেডি ইঞ্জিন এরর!"
                ],
                'default': [
                    "⚠️ কমান্ড এক্সিকিউট করতে সমস্যা!",
                    "🎯 অপারেশন ফেইলড! রিট্রাই করুন।",
                    "🤖 সিস্টেম এরর! প্লিজ ওয়েট।"
                ]
            }
            
            messages = error_variations.get(command, error_variations['default'])
            selected_message = random.choice(messages)
            
            if update and update.effective_message:
                # Random footer variations
                footer_variations = [
                    f"\n\n{self._get_random_word('for')} {self._get_random_word('help')}: /help",
                    f"\n\n{self._get_random_word('retry')}: /start",
                    f"\n\n{self._get_random_word('support')}: @{Config.BOT_USERNAME}"
                ]
                
                full_message = selected_message + random.choice(footer_variations)
                
                # Wrap with random border
                border = self._get_random_border()
                formatted_message = f"{border['top']}\n{full_message}\n{border['bottom']}"
                
                await update.effective_message.reply_text(
                    formatted_message,
                    parse_mode=ParseMode.HTML
                )
                
        except Exception as e:
            log_error(f"Error sending error message: {e}")
    
    # ==================== EXISTING METHODS (UNCHANGED) ====================
    # নিচের মেথডগুলো আপনার আসল কোড থেকে ঠিক রাখবেন
    
    def setup_application(self):
        """অ্যাপ্লিকেশন সেটআপ করে"""
        try:
            # Create application with optimized settings
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
            
            # Register all handlers
            self._register_all_handlers()
            
            # Register scheduled jobs
            self._register_scheduled_jobs()
            
            logger.info("✅ Application setup completed")
            return True
            
        except Exception as e:
            log_error(f"Application setup failed: {e}")
            return False
    
    def _register_all_handlers(self):
        """সকল হ্যান্ডলার রেজিস্টার করে"""
        try:
            # Command handlers - HTML parse_mode দিয়ে
            commands = [
                ("start", self.handle_start),
                ("help", self.handle_help),
                ("stats", self.handle_stats),
                ("leaderboard", self.handle_leaderboard),
                ("quote", self.handle_quote),
                ("roast", self.handle_roast_command),
                ("info", self.handle_info),
                ("ping", self.handle_ping),
            ]
            
            for cmd, handler in commands:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            # Admin commands
            admin_commands = [
                ("admin", self.handle_admin),
                ("broadcast", self.handle_broadcast),
                ("stats_full", self.handle_stats_full),
                ("cleanup", self.handle_cleanup),
            ]
            
            for cmd, handler in admin_commands:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            # Message handlers
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_text_message
            ))
            
            # Existing handlers...
            # ... [আপনার বাকি হ্যান্ডলারগুলো থাকবে]
            
            logger.info("✅ All handlers registered successfully")
            
        except Exception as e:
            log_error(f"Handler registration failed: {e}")
    
    def _validate_user_input(self, text: str, user_id: int, chat_id: int) -> bool:
        """ইউজার ইনপুট ভ্যালিডেট করে"""
        # Check cooldown
        if not self._check_user_cooldown(user_id, chat_id):
            return False
        
        # Check minimum length
        if len(text) < Config.MIN_INPUT_LENGTH:
            return False
        
        # Check safety
        if not safety_checker.is_safe_content(text):
            return False
        
        # Check for disallowed content
        if safety_checker.contains_disallowed_content(text):
            return False
        
        return True
    
    def _check_user_cooldown(self, user_id: int, chat_id: int) -> bool:
        """ইউজার কুলডাউন চেক করে"""
        key = f"{user_id}_{chat_id}"
        
        if key in self.user_cooldowns:
            last_time = self.user_cooldowns[key]
            time_diff = (TimeManager.get_current_time() - last_time).total_seconds()
            
            if time_diff < 2:  # 2 seconds cooldown
                return False
        
        self.user_cooldowns[key] = TimeManager.get_current_time()
        return True
    
    def _get_user_rank(self, user_id: int) -> int:
        """ইউজারের র‍্যাংক রিটার্ন করে"""
        try:
            with StorageManager.get_session() as db:
                # Get all users ordered by roast count
                users = db.query(User).order_by(User.roast_count.desc()).all()
                
                for i, user in enumerate(users, 1):
                    if user.user_id == user_id:
                        return i
                
                return len(users) + 1
        except:
            return 999
    
    # ... [আপনার বাকি মেথডগুলো থাকবে]

# ==================== MAIN FUNCTION ====================

async def main():
    """মেইন ফাংশন"""
    try:
        print("\n" + "="*60)
        print("🤖 ROASTIFY BOT - ADVANCED HTML VERSION")
        print("="*60)
        print(f"📅 {TimeManager.format_time()}")
        print("="*60 + "\n")
        
        # Create and run bot
        bot = RoastifyBot()
        await bot.start_bot()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  বট বন্ধ করা হচ্ছে (Ctrl+C)...")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n👋 Roastify Bot stopped")
        print("="*60)

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
