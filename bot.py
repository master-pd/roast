#!/usr/bin/env python3
"""
🤖 Roastify Telegram Bot - Complete & Advanced Version
✅ Random Borders | Random HTML | Multiple Templates | Professional
"""

import os
import sys
import asyncio
import random
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from io import BytesIO

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
    ChatMemberHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode, ChatAction

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
from database.models import init_database, User, Roast
from roast_engine.roaster import RoastEngine
from roast_engine.safety_check import safety_checker
from image_engine.image_generator import get_image_generator
from features.welcome_system import WelcomeSystem
from features.vote_system import VoteSystem
from features.mention_system import MentionSystem
from features.reaction_system import ReactionSystem
from features.admin_protection import AdminProtection
from features.auto_quotes import AutoQuoteSystem
from features.sticker_maker import StickerMaker
from features.quote_of_day import QuoteOfDay

class RoastifyBot:
    """রোস্টিফাই বট - Advanced Professional Version"""
    
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
            self.auto_quotes = AutoQuotes(self, self.quote_system)
            self.sticker_maker = StickerMaker()
            self.quote_of_day = QuoteOfDay()
            
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
                'images_sent': 0,
                'stickers_created': 0,
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
                "rainbow": {"top": "🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈", "bottom": "🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈"},
                "money": {"top": "💰💰💰💰💰💰💰💰💰💰", "bottom": "💰💰💰💰💰💰💰💰💰💰"},
                "trophy": {"top": "🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆", "bottom": "🏆🏆🏆🏆🏆🏆🏆🏆🏆🏆"},
                "comet": {"top": "☄️☄️☄️☄️☄️☄️☄️☄️☄️☄️", "bottom": "☄️☄️☄️☄️☄️☄️☄️☄️☄️☄️"},
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
                
                # Style 11: Card style
                lambda text, title: f'📄 <b>{title}</b>\n━━━━━━━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━━━━━━━',
                
                # Style 12: Star style
                lambda text, title: f'⭐ <b>{title}</b> ⭐\n\n{text}\n\n✨ Made with ❤️',
            ]
            
            # Random word variations
            self.word_variations = {
                "welcome": ["স্বাগতম", "আসসালামু আলাইকুম", "Welcome", "হ্যালো", "Hi there", "নমস্কার"],
                "help": ["সাহায্য", "হেল্প", "গাইড", "নির্দেশিকা", "ম্যানুয়াল"],
                "bot": ["বট", "Bot", "Robot", "স্বয়ংক্রিয়", "অটোমেটেড"],
                "roast": ["রোস্ট", "মজা", "জোক", "কমেডি", "ট্রল", "মসখোর"],
                "funny": ["মজার", "হাসির", "কৌতুক", "এন্টারটেইনমেন্ট", "কমিক"],
                "savage": ["স্যাভেজ", "কঠোর", "তীব্র", "বেপরোয়া", "রুড"],
                "enjoy": ["উপভোগ করুন", "এনজয়", "মজা নিন", "আনন্দ নিন", "ফান করুন"],
                "thanks": ["ধন্যবাদ", "Thank you", "শুকরিয়া", "মোবারক", "অনেক ধন্যবাদ"],
                "stats": ["পরিসংখ্যান", "স্ট্যাটস", "ডাটা", "তথ্য", "অ্যানালিটিক্স"],
                "leaderboard": ["লিডারবোর্ড", "শীর্ষ তালিকা", "টপ প্লেয়ার", "র‍্যাংকিং"],
                "quote": ["উক্তি", "কোট", "বাণী", "স্লোগান", "মেসেজ"],
                "ping": ["পিং", "লেটেন্সি", "রেসপন্স", "চেক", "টেস্ট"],
                "info": ["তথ্য", "ইনফো", "ডিটেইলস", "বিস্তারিত", "আরও জানুন"],
                "start": ["শুরু", "স্টার্ট", "শুরু করুন", "সক্রিয় করুন"],
                "ready": ["প্রস্তুত", "রেডি", "তৈরি", "সেট", "গোছানো"],
                "about": ["সম্পর্কে", "অ্যাবাউট", "বিস্তারিত", "পরিচয়"],
                "features": ["ফিচার", "বৈশিষ্ট্য", "সুবিধা", "ক্যাপাবিলিটি"],
                "commands": ["কমান্ড", "ইনস্ট্রাকশন", "নির্দেশাবলী", "মেনু"],
                "quick": ["দ্রুত", "কুইক", "ফাস্ট", "তাৎক্ষণিক"],
                "safety": ["নিরাপত্তা", "সেফটি", "প্রটেকশন", "সুরক্ষা"],
                "no": ["না", "নো", "নেই", "অনুপস্থিত"],
                "offensive": ["আপত্তিজনক", "অফেন্সিভ", "অশ্লীল", "খারাপ"],
                "content": ["কনটেন্ট", "বিষয়বস্তু", "ম্যাটেরিয়াল", "ডাটা"],
                "all": ["সব", "অল", "সমস্ত", "পুরো"],
                "fun": ["মজা", "ফান", "আনন্দ", "রমণ"],
                "respectful": ["সম্মানজনক", "রেসপেক্টফুল", "শালীন", "ভদ্র"],
                "roasts": ["রোস্ট", "মজা", "কমেডি", "জোকস"],
                "for": ["জন্য", "ফর", "উদ্দেশ্যে", "প্রতি"],
                "retry": ["আবার চেষ্টা করুন", "রিট্রাই", "পুনরায়", "নতুন করে"],
                "support": ["সাপোর্ট", "সহায়তা", "হেল্প", "সহযোগিতা"],
                "performance": ["পারফরম্যান্স", "কর্মদক্ষতা", "কার্যসম্পাদন", "কাজ"],
                "report": ["রিপোর্ট", "প্রতিবেদন", "বিবরণ", "ডাটা"],
                "analytics": ["অ্যানালিটিক্স", "বিশ্লেষণ", "স্ট্যাটিস্টিক্স", "তথ্যবিশ্লেষণ"],
                "user": ["ইউজার", "ব্যবহারকারী", "সদস্য", "অংশগ্রহণকারী"],
                "insights": ["ইনসাইট", "দৃষ্টিভঙ্গি", "বুঝ", "জ্ঞান"],
                "total": ["মোট", "টোটাল", "সর্বমোট", "সমষ্টি"],
                "votes": ["ভোট", "ভোটস", "রেটিং", "মূল্যায়ন"],
                "reactions": ["রিঅ্যাকশন", "প্রতিক্রিয়া", "ইমোজি", "প্রতিচ্ছবি"],
                "joined": ["যোগদান", "জয়েনড", "শুরু", "সদস্যপদ"],
                "activity": ["একটিভিটি", "কার্যকলাপ", "সক্রিয়তা", "ব্যবহার"],
                "updated": ["আপডেট", "আপডেটেড", "হালনাগাদ", "সাম্প্রতিক"],
                "not": ["না", "নট", "নেই", "অনুপস্থিত"],
                "found": ["পাওয়া গেছে", "ফাউন্ড", "মিলেছে", "দেখা গেছে"],
                "you": ["আপনি", "ইউ", "তুমি", "তোমাকে"],
                "havent": ["করেননি", "হ্যাভেন্ট", "না করা", "অসম্পূর্ণ"],
                "received": ["পেয়েছেন", "রিসিভড", "লাভ করেছেন", "প্রাপ্ত"],
                "any": ["কোন", "এনি", "যেকোন", "কিছু"],
                "yet": ["এখনও", "ইয়েট", "এখনো পর্যন্ত", "অদ্যাবধি"],
                "send": ["পাঠান", "সেন্ড", "প্রেরণ করুন", "দেখান"],
                "a": ["একটি", "এ", "এক", "কোনো"],
                "message": ["মেসেজ", "বার্তা", "মেসেজ", "কথা"],
                "to": ["থেকে", "টু", "প্রতি", "দিকে"],
                "get": ["পাবেন", "গেট", "লাভ করুন", "প্রাপ্তি"],
                "started": ["শুরু", "স্টার্টেড", "আরম্ভ", "চালু"],
                "latency": ["লেটেন্সি", "বিলম্ব", "সময়", "দেরি"],
                "status": ["স্ট্যাটাস", "অবস্থা", "হাল", "কন্ডিশন"],
                "time": ["সময়", "টাইম", "ঘড়ি", "মুহূর্ত"],
                "response": ["রেসপন্স", "প্রতিক্রিয়া", "উত্তর", "জবাব"],
                "bot": ["বট", "বট", "রোবট", "স্বয়ংক্রিয়"],
                "timestamp": ["টাইমস্ট্যাম্প", "সময়চিহ্ন", "তারিখসময়", "মুহূর্ত"],
                "brain": ["ব্রেন", "মস্তিষ্ক", "চিন্তা", "বুদ্ধি"],
                "overload": ["ওভারলোড", "অতিরিক্ত চাপ", "ভারবাহী", "অতিপ্রবাহ"],
                "restarting": ["রিস্টার্টিং", "পুনরায় শুরু", "নতুন করে শুরু", "রিবুট"],
                "oops": ["উফ", "ওফ", "ওহো", "আরে"],
                "something": ["কিছু", "সামথিং", "কোনো কিছু", "একটা"],
                "went": ["গেছে", "ওয়েন্ট", "চলে গেছে", "হয়ে গেছে"],
                "wrong": ["ভুল", "রং", "ত্রুটি", "সমস্যা"],
                "technical": ["টেকনিক্যাল", "প্রযুক্তিগত", "কারিগরি", "টেক"],
                "difficulty": ["সমস্যা", "ডিফিকালটি", "কঠিনতা", "জটিলতা"],
                "please": ["দয়া করে", "প্লিজ", "অনুগ্রহ করে", "করুন"],
                "wait": ["অপেক্ষা করুন", "ওয়েট", "ধৈর্য ধরে", "প্রতীক্ষা"],
                "system": ["সিস্টেম", "পদ্ধতি", "ব্যবস্থা", "যন্ত্র"],
                "error": ["এরর", "ত্রুটি", "ভুল", "সমস্যা"],
                "recovering": ["রিকভারিং", "পুনরুদ্ধার", "সামলে নিচ্ছি", "ঠিক করছি"],
            }
            
            logger.info("✅ RoastifyBot Advanced HTML Version initialized")
            logger.info(f"🤖 Bot: @{Config.BOT_USERNAME}")
            logger.info(f"👑 Owner: {Config.OWNER_ID}")
            logger.info("=" * 50)
            
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
    
    # ==================== COMMAND HANDLERS ====================
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start command"""
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
                f"স্বাগতম {user.first_name}! মজা শুরু করি?",
                f"নমস্কার {user.first_name}! রোস্ট টাইম!",
                f"Hello {user.first_name}! কমেডি মোড চালু!",
            ]
            
            help_variations = [
                "শুধু মেসেজ লিখুন → রোস্ট পাবেন",
                "Just type a message → Get roasted",
                "গ্রুপে মেনশন করুন → ইন্সট্যান্ট রোস্ট",
                "Use /roast for instant roast",
                "ভোট দিয়ে রেটিং দিন → লিডারবোর্ডে উঠুন",
                "মজা করতে কোনো মেসেজ লিখুন",
                "টেক্সট দিয়ে রোস্ট জেনারেট করুন",
            ]
            
            # Create random HTML message
            welcome_html = self._format_random_html_message(
                title=random.choice(["welcome", "hello", "hi", "greetings", "start"]),
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
                    f"/quote - {self._get_random_word('quote')}\n"
                    f"/leaderboard - {self._get_random_word('leaderboard')}\n"
                    f"/ping - {self._get_random_word('ping')}\n\n"
                    
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
                    user_id=user.id,
                    style="welcome"
                )
                
                if image:
                    # Convert to bytes
                    image_bytes = self.image_generator.image_to_bytes(image)
                    
                    await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=image_bytes,
                        caption=welcome_html,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await update.message.reply_text(welcome_html, parse_mode=ParseMode.HTML)
                    
            except Exception as e:
                logger.warning(f"Could not send welcome image: {e}")
                await update.message.reply_text(welcome_html, parse_mode=ParseMode.HTML)
            
            self.stats['total_messages'] += 1
            logger.info(f"User {user.id} started the bot")
            
        except Exception as e:
            log_error(f"Error in handle_start: {e}")
            await self._send_error_message(update, "start")
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/help command"""
        try:
            # Random help content variations
            about_variations = [
                "আমি একটি এডভান্সড রোস্ট বট",
                "I'm an advanced roast bot",
                "স্মার্ট রোস্ট জেনারেশন",
                "AI-powered roast generation",
                "প্রফেশনাল কমেডি সার্ভিস",
                "ইন্টেলিজেন্ট রোস্ট মেশিন",
                "সবচেয়ে মজার রোস্ট বট",
            ]
            
            feature_variations = [
                "ইমেজ সহ রোস্ট",
                "ভোট সিস্টেম",
                "লিডারবোর্ড",
                "র‍্যান্ডম রোস্ট",
                "গ্রুপ সাপোর্ট",
                "স্টিকার তৈরি",
                "ডেইলি কোটস",
                "র‍্যান্ডম টেমপ্লেট",
            ]
            
            command_variations = [
                "/roast - ইন্সট্যান্ট রোস্ট",
                "/stats - পার্সোনাল স্ট্যাটস", 
                "/leaderboard - টপ প্লেয়ার",
                "/quote - ইনস্পিরেশনাল কোট",
                "/ping - বট চেক",
                "/sticker - ইমেজ থেকে স্টিকার",
                "/info - বট সম্পর্কে",
                "/daily - আজকের রোস্ট",
            ]
            
            # Random HTML message
            help_html = self._format_random_html_message(
                title=random.choice(["help", "guide", "manual", "instructions", "support"]),
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
        """/stats command"""
        try:
            user = update.effective_user
            
            # Get user stats from database
            with StorageManager.get_session() as db:
                user_record = db.query(User).filter(User.user_id == user.id).first()
                
                if user_record:
                    # Calculate rank
                    rank = self._get_user_rank(user.id)
                    
                    # Random stat variations
                    stat_variations = [
                        f"📊 {user.first_name}'র {self._get_random_word('stats')}",
                        f"📈 {self._get_random_word('performance')} {self._get_random_word('report')}",
                        f"🎯 {user.first_name}'র {self._get_random_word('analytics')}",
                        f"📋 {self._get_random_word('user')} {self._get_random_word('stats')}",
                        f"🔍 {self._get_random_word('insights')} {self._get_random_word('for')} {user.first_name}"
                    ]
                    
                    stats_html = self._format_random_html_message(
                        title=random.choice(stat_variations),
                        content=(
                            f"• {self._get_random_word('total')} {self._get_random_word('roasts')}: <code>{user_record.roast_count}</code>\n"
                            f"• {self._get_random_word('total')} {self._get_random_word('votes')}: <code>{user_record.vote_count}</code>\n"
                            f"• {self._get_random_word('reactions')}: <code>{user_record.reaction_count}</code>\n"
                            f"• {self._get_random_word('joined')}: <code>{TimeManager.format_time(user_record.created_at)}</code>\n"
                            f"• {self._get_random_word('last')} {self._get_random_word('active')}: <code>{TimeManager.format_time(user_record.last_active)}</code>\n\n"
                            
                            f"🏆 {self._get_random_word('rank')}: <code>#{rank}</code>\n"
                            f"🔥 {self._get_random_word('activity')}: <code>{self._get_random_word('active') if rank <= 100 else self._get_random_word('normal')}</code>"
                        ),
                        footer=f"📅 {self._get_random_word('updated')}: {TimeManager.format_time()}",
                        add_border=True
                    )
                else:
                    stats_html = self._format_random_html_message(
                        title=random.choice(["stats", "analytics", "data", "information"]),
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
    
    async def handle_roast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/roast command"""
        try:
            user = update.effective_user
            chat = update.effective_chat
            
            # Generate random roast
            roast_data = self.roast_engine.generate_roast(user_id=user.id)
            
            # Send typing action
            await context.bot.send_chat_action(
                chat_id=chat.id,
                action="upload_photo"
            )
            
            # Create and send image
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=f"{user.first_name}'র রোস্ট | /roast",
                user_id=user.id,
                style="random"
            )
            
            if image:
                image_bytes = self.image_generator.image_to_bytes(image)
                
                # Random captions
                captions = [
                    f"🔥 {self._get_random_word('here')} {self._get_random_word('is')} {self._get_random_word('your')} {self._get_random_word('roast')}!",
                    f"🎯 {self._get_random_word('roast')} {self._get_random_word('delivered')}!",
                    f"⚡ {self._get_random_word('fresh')} {self._get_random_word('roast')} {self._get_random_word('for')} {user.first_name}!",
                    f"😈 {self._get_random_word('enjoy')} {self._get_random_word('this')} {self._get_random_word('one')}!",
                    f"💀 {self._get_random_word('savage')} {self._get_random_word('mode')} {self._get_random_word('activated')}!"
                ]
                
                sent_message = await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=image_bytes,
                    caption=random.choice(captions),
                    parse_mode=ParseMode.HTML
                )
                
                # Add vote buttons
                await self.vote_system.add_vote_to_message(
                    update, context, sent_message.message_id, chat.id
                )
                
                self.stats['images_sent'] += 1
                self.stats['total_roasts'] += 1
                
                # Update database
                StorageManager.get_or_create_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
                
                StorageManager.increment_user_roast_count(user.id)
                
                logger.info(f"Command roast for user {user.id}")
                
            else:
                # Fallback text response
                await update.message.reply_text(
                    f"🔥 *রোস্ট টাইম!*\n\n{roast_data['primary']}\n\n{roast_data['secondary']}",
                    parse_mode=ParseMode.HTML
                )
            
        except Exception as e:
            log_error(f"Error in handle_roast_command: {e}")
            await self._send_error_message(update, "roast")
    
    async def handle_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/leaderboard command"""
        try:
            # Get leaderboard from database
            with StorageManager.get_session() as db:
                top_users = db.query(User).order_by(User.roast_count.desc()).limit(10).all()
            
            if not top_users:
                leaderboard_html = self._format_random_html_message(
                    title=self._get_random_word("leaderboard"),
                    content="😴 এখনো কেউ রোস্ট করেনি! প্রথম হওয়ার সুযোগ নিন!",
                    footer=f"🚀 {self._get_random_word('start')}: /roast",
                    add_border=True
                )
            else:
                # Create leaderboard text
                leaderboard_text = ""
                medals = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
                
                for i, user in enumerate(top_users):
                    if i < 3:
                        medal = medals[i]
                    else:
                        medal = medals[i]
                    
                    username = user.username or f"User_{user.user_id}"
                    leaderboard_text += f"{medal} {username} - <code>{user.roast_count}</code> রোস্ট\n"
                
                leaderboard_html = self._format_random_html_message(
                    title=random.choice(["🏆 লিডারবোর্ড", "🔥 টপ রোস্টার", "🎯 শীর্ষ খেলোয়াড়", "⭐ সেরা সদস্য"]),
                    content=leaderboard_text,
                    footer=f"📊 {self._get_random_word('updated')}: {TimeManager.format_time()}",
                    add_border=True
                )
            
            await update.message.reply_text(leaderboard_html, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            log_error(f"Error in handle_leaderboard: {e}")
            await self._send_error_message(update, "leaderboard")
    
    async def handle_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/quote command"""
        try:
            # Get random quote
            quote = self.quote_of_day.get_todays_quote()
            
            quote_html = self._format_random_html_message(
                title=random.choice(["💬 উক্তি", "✨ ইনস্পিরেশন", "📜 বাণী", "🌟 মোটিভেশন"]),
                content=f"\"{quote['text']}\"\n\n— <i>{quote['author']}</i>",
                footer=f"📅 {self._get_random_word('quote')} {self._get_random_word('of')} {self._get_random_word('the')} {self._get_random_word('day')}",
                add_border=True
            )
            
            await update.message.reply_text(quote_html, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            log_error(f"Error in handle_quote: {e}")
            await self._send_error_message(update, "quote")
    
    async def handle_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/ping command"""
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
    
    async def handle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/info command"""
        try:
            uptime = TimeManager.get_current_time() - self.stats['start_time']
            uptime_str = str(uptime).split('.')[0]
            
            info_html = self._format_random_html_message(
                title="🤖 Roastify Bot - Info",
                content=(
                    f"📊 <u>স্ট্যাটিস্টিক্স:</u>\n"
                    f"• {self._get_random_word('total')} {self._get_random_word('messages')}: <code>{self.stats['total_messages']}</code>\n"
                    f"• {self._get_random_word('total')} {self._get_random_word('roasts')}: <code>{self.stats['total_roasts']}</code>\n"
                    f"• {self._get_random_word('images')}: <code>{self.stats['images_sent']}</code>\n"
                    f"• {self._get_random_word('uptime')}: <code>{uptime_str}</code>\n\n"
                    
                    f"⚙️ <u>টেকনোলজি:</u>\n"
                    f"• Python Telegram Bot\n"
                    f"• Advanced HTML Formatting\n"
                    f"• Random Templates & Borders\n"
                    f"• Professional Image Generation\n\n"
                    
                    f"👑 <u>ইনফরমেশন:</u>\n"
                    f"• {self._get_random_word('owner')}: <code>{Config.OWNER_ID}</code>\n"
                    f"• {self._get_random_word('bot')}: @{Config.BOT_USERNAME}\n"
                    f"• {self._get_random_word('version')}: <code>3.0.0</code>"
                ),
                footer=f"🔥 {self._get_random_word('fun')} {self._get_random_word('with')} {self._get_random_word('roasts')}!",
                add_border=True
            )
            
            await update.message.reply_text(info_html, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            log_error(f"Error in handle_info: {e}")
            await self._send_error_message(update, "info")
    
    async def handle_sticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/sticker command - create sticker from image"""
        try:
            user = update.effective_user
            
            if not update.message.reply_to_message or not update.message.reply_to_message.photo:
                await update.message.reply_text(
                    self._format_random_html_message(
                        title="❌ স্টিকার তৈরি",
                        content=f"দয়া করে একটি ইমেজে রিপ্লাই দিয়ে /sticker কমান্ড ব্যবহার করুন!",
                        footer=f"📸 {self._get_random_word('reply')} {self._get_random_word('to')} {self._get_random_word('image')}",
                        add_border=True
                    ),
                    parse_mode=ParseMode.HTML
                )
                return
            
            # Create sticker
            sticker_file = await self.sticker_maker.create_sticker_from_message(
                update.message.reply_to_message
            )
            
            if sticker_file:
                await context.bot.send_sticker(
                    chat_id=update.effective_chat.id,
                    sticker=sticker_file
                )
                
                self.stats['stickers_created'] += 1
                logger.info(f"Sticker created for user {user.id}")
            else:
                await update.message.reply_text(
                    self._format_random_html_message(
                        title="❌ স্টিকার তৈরি",
                        content=f"স্টিকার তৈরি করতে সমস্যা হয়েছে! দয়া করে আবার চেষ্টা করুন।",
                        footer=f"🔄 {self._get_random_word('retry')}",
                        add_border=True
                    ),
                    parse_mode=ParseMode.HTML
                )
            
        except Exception as e:
            log_error(f"Error in handle_sticker: {e}")
            await self._send_error_message(update, "sticker")
    
    # ==================== TEXT MESSAGE HANDLER ====================
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
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
            image_styles = ["default", "funny", "savage", "welcome", "vibrant", "modern", "cyberpunk", "vintage"]
            random_style = random.choice(image_styles)
            
            # Create and send image with random variations
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id,
                style=random_style
            )
            
            if image:
                image_bytes = self.image_generator.image_to_bytes(image)
                
                # Random captions
                captions = [
                    f"🔥 {self._get_random_word('here')} {self._get_random_word('is')} {self._get_random_word('your')} {self._get_random_word('roast')}!",
                    f"🎯 {self._get_random_word('roast')} {self._get_random_word('delivered')}!",
                    f"⚡ {self._get_random_word('fresh')} {self._get_random_word('roast')} {self._get_random_word('for')} {user.first_name}!",
                    f"😈 {self._get_random_word('enjoy')} {self._get_random_word('this')} {self._get_random_word('one')}!",
                    f"💀 {self._get_random_word('savage')} {self._get_random_word('mode')} {self._get_random_word('activated')}!"
                ]
                
                sent_message = await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=image_bytes,
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
    
    # ==================== ADMIN COMMANDS ====================
    
    async def handle_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/admin command"""
        try:
            user = update.effective_user
            
            # Check if user is owner
            if str(user.id) != str(Config.OWNER_ID):
                await update.message.reply_text(
                    self._format_random_html_message(
                        title="❌ অ্যাক্সেস ডিনাইড",
                        content="শুধুমাত্র ওনার এই কমান্ড ব্যবহার করতে পারবেন!",
                        footer=f"👑 {self._get_random_word('owner')}: {Config.OWNER_ID}",
                        add_border=True
                    ),
                    parse_mode=ParseMode.HTML
                )
                return
            
            # Get admin stats
            with StorageManager.get_session() as db:
                total_users = db.query(User).count()
                total_roasts = db.query(Roast).count()
                active_today = db.query(User).filter(
                    User.last_active >= TimeManager.get_current_time().replace(hour=0, minute=0, second=0)
                ).count()
            
            admin_html = self._format_random_html_message(
                title="👑 অ্যাডমিন প্যানেল",
                content=(
                    f"📊 <u>সিস্টেম স্ট্যাটস:</u>\n"
                    f"• {self._get_random_word('total')} {self._get_random_word('users')}: <code>{total_users}</code>\n"
                    f"• {self._get_random_word('total')} {self._get_random_word('roasts')}: <code>{total_roasts}</code>\n"
                    f"• {self._get_random_word('active')} {self._get_random_word('today')}: <code>{active_today}</code>\n"
                    f"• {self._get_random_word('bot')} {self._get_random_word('messages')}: <code>{self.stats['total_messages']}</code>\n\n"
                    
                    f"⚡ <u>অ্যাডমিন কমান্ডস:</u>\n"
                    f"/broadcast - বার্তা পাঠান\n"
                    f"/stats_full - বিস্তারিত স্ট্যাটস\n"
                    f"/cleanup - ডাটাবেস ক্লিনআপ\n"
                    f"/info - বট ইনফো"
                ),
                footer=f"🤖 {self._get_random_word('bot')}: @{Config.BOT_USERNAME}",
                add_border=True
            )
            
            await update.message.reply_text(admin_html, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            log_error(f"Error in handle_admin: {e}")
            await self._send_error_message(update, "admin")
    
    async def handle_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/broadcast command"""
        try:
            user = update.effective_user
            
            # Check if user is owner
            if str(user.id) != str(Config.OWNER_ID):
                return
            
            # Get message text
            if not context.args:
                await update.message.reply_text(
                    "ব্যবহার: /broadcast <message>",
                    parse_mode=ParseMode.HTML
                )
                return
            
            message_text = ' '.join(context.args)
            
            # Get all users
            with StorageManager.get_session() as db:
                users = db.query(User).all()
            
            # Send broadcast
            sent_count = 0
            failed_count = 0
            
            await update.message.reply_text(f"📢 ব্রডকাস্ট শুরু... ({len(users)} ইউজার)")
            
            for user_record in users:
                try:
                    await context.bot.send_message(
                        chat_id=user_record.user_id,
                        text=f"📢 <b>ব্রডকাস্ট মেসেজ:</b>\n\n{message_text}\n\n— @{Config.BOT_USERNAME}",
                        parse_mode=ParseMode.HTML
                    )
                    sent_count += 1
                    
                    # Delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    failed_count += 1
                    logger.warning(f"Failed to send broadcast to {user_record.user_id}: {e}")
            
            await update.message.reply_text(
                f"✅ ব্রডকাস্ট সম্পন্ন!\n\nসেন্ট: {sent_count}\nফেইলড: {failed_count}",
                parse_mode=ParseMode.HTML
            )
            
        except Exception as e:
            log_error(f"Error in handle_broadcast: {e}")
            await self._send_error_message(update, "broadcast")
    
    # ==================== HELPER METHODS ====================
    
    def _validate_user_input(self, text: str, user_id: int, chat_id: int) -> bool:
        """Validate user input"""
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
        """Check user cooldown"""
        key = f"{user_id}_{chat_id}"
        current_time = TimeManager.get_current_time()
        
        if key in self.user_cooldowns:
            last_time = self.user_cooldowns[key]
            time_diff = (current_time - last_time).total_seconds()
            
            if time_diff < Config.COOLDOWN_SECONDS:
                return False
        
        self.user_cooldowns[key] = current_time
        return True
    
    def _get_user_rank(self, user_id: int) -> int:
        """Get user rank"""
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
    
    async def _send_error_message(self, update: Update, command: str):
        """Send error message"""
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
    
    # ==================== BOT CONTROL METHODS ====================
    
    def setup_application(self):
        """Setup Telegram application"""
        try:
            # Create application
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
            
            # Register error handler
            self.application.add_error_handler(self._handle_error)
            
            logger.info("✅ Application setup completed")
            return True
            
        except Exception as e:
            log_error(f"Application setup failed: {e}")
            return False
    
    def _register_all_handlers(self):
        """Register all handlers"""
        try:
            # Command handlers
            commands = [
                ("start", self.handle_start),
                ("help", self.handle_help),
                ("stats", self.handle_stats),
                ("roast", self.handle_roast_command),
                ("leaderboard", self.handle_leaderboard),
                ("quote", self.handle_quote),
                ("ping", self.handle_ping),
                ("info", self.handle_info),
                ("sticker", self.handle_sticker),
            ]
            
            for cmd, handler in commands:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            # Admin commands
            admin_commands = [
                ("admin", self.handle_admin),
                ("broadcast", self.handle_broadcast),
            ]
            
            for cmd, handler in admin_commands:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            # Message handlers
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_text_message
            ))
            
            # Callback query handler for votes
            self.application.add_handler(CallbackQueryHandler(
                self.vote_system.handle_vote_callback
            ))
            
            logger.info("✅ All handlers registered successfully")
            
        except Exception as e:
            log_error(f"Handler registration failed: {e}")
    
    async def _set_bot_commands(self):
        """Set bot commands for menu"""
        try:
            commands = [
                BotCommand("start", "বট শুরু করুন"),
                BotCommand("help", "সাহায্য পান"),
                BotCommand("roast", "রোস্ট পান"),
                BotCommand("stats", "আপনার স্ট্যাটস"),
                BotCommand("leaderboard", "লিডারবোর্ড দেখুন"),
                BotCommand("quote", "ইনস্পিরেশনাল কোট পান"),
                BotCommand("ping", "বট চেক করুন"),
                BotCommand("info", "বট তথ্য"),
                BotCommand("sticker", "ইমেজ থেকে স্টিকার"),
            ]
            
            await self.application.bot.set_my_commands(commands)
            logger.info("✅ Bot commands set successfully")
            
        except Exception as e:
            logger.error(f"Failed to set bot commands: {e}")
    
    async def _handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors globally"""
        try:
            self.stats['total_errors'] += 1
            
            error_msg = str(context.error)[:200]
            logger.error(f"Bot error: {error_msg}")
            
            # Notify owner
            if Config.OWNER_ID:
                try:
                    await context.bot.send_message(
                        chat_id=Config.OWNER_ID,
                        text=f"⚠️ <b>Bot Error:</b>\n\n<code>{error_msg}</code>",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error handler error: {e}")
    
    # ==================== MAIN RUN METHOD ====================
    
    async def run(self):
        """Run the bot (main entry point)"""
        try:
            logger.info("🚀 Starting Roastify Bot...")
            
            # Setup application
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
            await self.stop()
    
    async def _keep_running(self):
        """Keep bot running"""
        try:
            # Run forever until interrupted
            while self.is_running:
                await asyncio.sleep(1)
                
                # Log status every 5 minutes
                current_time = TimeManager.get_current_time()
                if current_time.minute % 5 == 0 and current_time.second == 0:
                    logger.info(f"📊 Status: Messages: {self.stats['total_messages']} | Roasts: {self.stats['total_roasts']} | Errors: {self.stats['total_errors']}")
                    
        except asyncio.CancelledError:
            logger.info("Bot stopped by cancellation")
        except Exception as e:
            logger.error(f"Error in keep_running: {e}")
    
    async def stop(self):
        """Stop the bot"""
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
    """Main function"""
    try:
        print("\n" + "="*60)
        print("🤖 ROASTIFY BOT - ADVANCED HTML VERSION")
        print("="*60)
        print(f"📅 {TimeManager.format_time()}")
        print("="*60 + "\n")
        
        # Create and run bot
        bot = RoastifyBot()
        await bot.run()
        
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
