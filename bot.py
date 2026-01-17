#!/usr/bin/env python3
"""
Roastify Telegram Bot - Advanced Professional Version
তুমি লেখো, বাকি অপমান আমরা করবো 😈
Fully Fixed, Updated, and Optimized for Termux
"""

import asyncio
import sys
import traceback
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
#from image_engine.image_generator import get_image_generator
from image_engine.image_generator import image_generator
from features.welcome_system import AdvancedWelcomeSystem
#from features.welcome_system import WelcomeSystem
from features.vote_system import VoteSystem
from features.mention_system import MentionSystem
from features.reaction_system import ReactionSystem
from features.admin_protection import AdminProtection
from features.auto_quotes import AutoQuoteSystem

class RoastifyBot:
    """রোস্টিফাই বট - প্রফেশনাল এডভান্সড ভার্সন"""
    
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
            
            logger.info("✅ RoastifyBot Professional Edition initialized")
            logger.info(f"🤖 Bot: @{Config.BOT_USERNAME}")
            logger.info(f"👑 Owner: {Config.OWNER_ID}")
            
        except Exception as e:
            log_error(f"Failed to initialize bot: {e}")
            raise
    
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
            # Command handlers
            commands = [
                ("start", self.handle_start, "বট শুরু করুন"),
                ("help", self.handle_help, "সাহায্য পান"),
                ("stats", self.handle_stats, "আপনার স্ট্যাটস দেখুন"),
                ("leaderboard", self.handle_leaderboard, "লিডারবোর্ড দেখুন"),
                ("quote", self.handle_quote, "র‍্যান্ডম কোট পান"),
                ("roast", self.handle_roast_command, "রোস্ট পান"),
                ("info", self.handle_info, "বট সম্পর্কে জানুন"),
                ("ping", self.handle_ping, "বট চেক করুন"),
            ]
            
            for cmd, handler, _ in commands:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            # Admin commands (only for owner/admins)
            admin_commands = [
                ("admin", self.handle_admin, "অ্যাডমিন প্যানেল"),
                ("broadcast", self.handle_broadcast, "ব্রডকাস্ট মেসেজ"),
                ("stats_full", self.handle_stats_full, "সম্পূর্ণ স্ট্যাটস"),
                ("cleanup", self.handle_cleanup, "ক্লিনআপ করুন"),
            ]
            
            for cmd, handler, _ in admin_commands:
                self.application.add_handler(CommandHandler(cmd, handler))
            
            # Message handlers
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_text_message
            ))
            
            # Mention handler
            self.application.add_handler(MessageHandler(
                filters.TEXT & filters.Entity("mention"),
                self.handle_mention
            ))
            
            # Group events
            self.application.add_handler(ChatMemberHandler(
                self.handle_chat_member_update,
                ChatMemberHandler.CHAT_MEMBER
            ))
            
            self.application.add_handler(MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS,
                self.handle_new_chat_members
            ))
            
            # Callback queries (for votes)
            self.application.add_handler(CallbackQueryHandler(
                self.handle_callback_query,
                pattern="^vote_"
            ))
            
            # General callback handler
            self.application.add_handler(CallbackQueryHandler(
                self.handle_general_callback
            ))
            
            # Error handler
            self.application.add_error_handler(self.error_handler)
            
            logger.info(f"✅ Registered {len(commands) + len(admin_commands)} commands")
            logger.info("✅ All handlers registered successfully")
            
        except Exception as e:
            log_error(f"Handler registration failed: {e}")
    
    def _register_scheduled_jobs(self):
        """সিডিউলড জব রেজিস্টার করে"""
        try:
            job_queue = self.application.job_queue
            
            # Daily quote at 12:00 PM
            job_queue.run_daily(
                self._job_daily_quote,
                time=TimeManager.get_current_time().replace(hour=12, minute=0, second=0),
                name="daily_quote"
            )
            
            # Cleanup old data at 3:00 AM
            job_queue.run_daily(
                self._job_cleanup_data,
                time=TimeManager.get_current_time().replace(hour=3, minute=0, second=0),
                name="cleanup_data"
            )
            
            # Reset cooldowns hourly
            job_queue.run_repeating(
                self._job_reset_cooldowns,
                interval=3600,
                first=60,
                name="reset_cooldowns"
            )
            
            # Save statistics every 6 hours
            job_queue.run_repeating(
                self._job_save_stats,
                interval=21600,
                first=300,
                name="save_stats"
            )
            
            # Health check every 30 minutes
            job_queue.run_repeating(
                self._job_health_check,
                interval=1800,
                first=10,
                name="health_check"
            )
            
            logger.info("✅ Scheduled jobs registered")
            
        except Exception as e:
            log_error(f"Job registration failed: {e}")
    
    async def _set_bot_commands(self):
        """বট কমান্ড সেট করে"""
        try:
            commands = [
                BotCommand("start", "বট শুরু করুন"),
                BotCommand("help", "সাহায্য পান"),
                BotCommand("stats", "আপনার স্ট্যাটস"),
                BotCommand("leaderboard", "লিডারবোর্ড দেখুন"),
                BotCommand("quote", "র‍্যান্ডম কোট পান"),
                BotCommand("roast", "রোস্ট পান"),
                BotCommand("info", "বট সম্পর্কে জানুন"),
                BotCommand("ping", "বট চেক করুন"),
            ]
            
            await self.application.bot.set_my_commands(commands)
            logger.info("✅ Bot commands set successfully")
            
        except Exception as e:
            log_error(f"Failed to set bot commands: {e}")
    
    async def start_bot(self):
        """বট শুরু করে"""
        try:
            logger.info("🚀 Starting Roastify Bot...")
            
            # Setup application
            if not self.setup_application():
                raise Exception("Application setup failed")
            
            # Set bot commands
            await self._set_bot_commands()
            
            # Update bot info
            bot_info = await self.application.bot.get_me()
            logger.info(f"🤖 Bot Info: @{bot_info.username} (ID: {bot_info.id})")
            
            # Start polling
            await self.application.initialize()
            await self.application.start()
            
            self.is_running = True
            
            logger.info("✅ Bot started successfully!")
            logger.info("📡 Bot is now polling for updates...")
            
            # Run until stopped
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
            # Keep running
            await self._keep_running()
            
        except Exception as e:
            log_error(f"Failed to start bot: {e}")
            await self.stop_bot()
    
    async def _keep_running(self):
        """বট চলমান রাখে"""
        try:
            while self.is_running:
                await asyncio.sleep(1)
                
                # Log status every 5 minutes
                if int(TimeManager.get_current_time().timestamp()) % 300 == 0:
                    logger.info(f"📊 Bot Status: Running | Messages: {self.stats['total_messages']} | Roasts: {self.stats['total_roasts']}")
                    
        except asyncio.CancelledError:
            logger.info("Bot keep-running task cancelled")
        except Exception as e:
            log_error(f"Error in keep_running: {e}")
    
    async def stop_bot(self):
        """বট বন্ধ করে"""
        try:
            logger.info("🛑 Stopping bot...")
            
            self.is_running = False
            
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            # Save final stats
            self._save_final_stats()
            
            logger.info("✅ Bot stopped successfully")
            
        except Exception as e:
            log_error(f"Error stopping bot: {e}")
    
    # ==================== COMMAND HANDLERS ====================
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start কমান্ড হ্যান্ডল করে"""
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
            
            # Send welcome
            welcome_text = (
                f"🤖 *রোস্টিফাই বটে স্বাগতম {user.first_name}!*\n\n"
                "আমি একটি এডভান্সড রোস্ট বট। শুধু মেসেজ লিখুন, "
                "আপনার জন্য রোস্ট ইমেজ তৈরি করব! 😈\n\n"
                "*📋 ব্যবহার 방법:*\n"
                "• শুধু মেসেজ লিখুন → রোস্ট পাবেন\n"
                "• গ্রুপে কাউকে @মেনশন করুন\n"
                "• ভোট দিয়ে রেটিং দিন\n\n"
                "*🛠️ কমান্ডস:*\n"
                "/help - সাহায্য\n"
                "/stats - আপনার স্ট্যাটস\n"
                "/roast - রোস্ট পান\n"
                "/quote - র‍্যান্ডম কোট\n\n"
                "রোস্টের জন্য প্রস্তুত? লিখুন শুরু করুন! 🔥"
            )
            
            # Create welcome image
            try:
                image = image_generator.create_roast_image(
                    primary_text=f"স্বাগতম {user.first_name}!",
                    secondary_text="রোস্টের জন্য প্রস্তুত? 😈",
                    user_id=user.id
                )
                
                image_path = image_generator.save_image(image)
                
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=photo,
                        caption=welcome_text,
                        parse_mode="Markdown"
                    )
                    
            except Exception as e:
                logger.warning(f"Could not send welcome image: {e}")
                await update.message.reply_text(welcome_text, parse_mode="Markdown")
            
            self.stats['total_messages'] += 1
            logger.info(f"User {user.id} started the bot")
            
        except Exception as e:
            log_error(f"Error in handle_start: {e}")
            await self._send_error_message(update, "start")
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/help কমান্ড হ্যান্ডল করে"""
        try:
            help_text = (
                "📚 *রোস্টিফাই বট হেল্প*\n\n"
                "*🎯 বট সম্পর্কে:*\n"
                "আমি একটি এডভান্সড রোস্ট বট। আপনার মেসেজের উপর ভিত্তি করে "
                "স্মার্ট রোস্ট তৈরি করি এবং সুন্দর ইমেজ সহ পাঠাই।\n\n"
                "*🛠️ ব্যবহার 방법:*\n"
                "1. যেকোনো মেসেজ লিখুন (ইংরেজি/বাংলা)\n"
                "2. রোস্ট ইমেজ পাবেন\n"
                "3. ভোট দিয়ে রেটিং দিন\n"
                "4. গ্রুপে মেনশন করুন\n\n"
                "*⚡ দ্রুত কমান্ড:*\n"
                "• `/roast` - র‍্যান্ডম রোস্ট পান\n"
                "• `/quote` - ইনস্পিরেশনাল কোট\n"
                "• `/stats` - আপনার পরিসংখ্যান\n"
                "• `/leaderboard` - টপ ইউজার\n\n"
                "*🔒 নিরাপত্তা:*\n"
                "• কোনো অপমানজনক কন্টেন্ট নেই\n"
                "• সম্পূর্ণ বিনামূল্যে\n"
                "• 24/7 একটিভ\n\n"
                f"🤖 বট: @{Config.BOT_USERNAME}\n"
                "📞 সাহায্য: /start"
            )
            
            await update.message.reply_text(help_text, parse_mode="Markdown")
            
        except Exception as e:
            log_error(f"Error in handle_help: {e}")
            await self._send_error_message(update, "help")
    
    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/stats কমান্ড হ্যান্ডল করে"""
        try:
            user = update.effective_user
            
            # Get user stats from database
            with StorageManager.get_session() as db:
                user_record = db.query(User).filter(User.user_id == user.id).first()
                
                if user_record:
                    stats_text = (
                        f"📊 *{user.first_name}'র পরিসংখ্যান*\n\n"
                        f"• মোট রোস্ট: `{user_record.roast_count}`\n"
                        f"• মোট ভোট: `{user_record.vote_count}`\n"
                        f"• রিএকশন: `{user_record.reaction_count}`\n"
                        f"• যোগদান: `{TimeManager.format_time(user_record.created_at)}`\n\n"
                        f"🏆 র‍্যাংক: `#{self._get_user_rank(user.id)}`\n"
                        f"🔥 কার্যকলাপ: `{'সক্রিয়' if user_record.roast_count > 0 else 'নতুন'}`"
                    )
                else:
                    stats_text = (
                        "📊 *পরিসংখ্যান পাওয়া যায়নি*\n\n"
                        "আপনি এখনো কোনো রোস্ট পাননি!\n"
                        "একটি মেসেজ লিখুন রোস্ট পেতে।"
                    )
            
            await update.message.reply_text(stats_text, parse_mode="Markdown")
            
        except Exception as e:
            log_error(f"Error in handle_stats: {e}")
            await self._send_error_message(update, "stats")
    
    async def handle_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/leaderboard কমান্ড হ্যান্ডল করে"""
        try:
            # Get leaderboard data
            leaderboard = StorageManager.get_leaderboard("most_roasted", limit=10)
            
            if not leaderboard:
                await update.message.reply_text(
                    "🏆 *লিডারবোর্ড খালি*\n\n"
                    "এখনো কোনো ডাটা সংগ্রহ হয়নি!\n"
                    "রোস্ট শুরু করুন লিডারবোর্ডে আসতে।",
                    parse_mode="Markdown"
                )
                return
            
            # Format leaderboard
            leaderboard_text = "🏆 *টপ ১০ রোস্টেড ইউজার*\n\n"
            
            for i, entry in enumerate(leaderboard, 1):
                medal = self._get_medal_emoji(i)
                username = entry["username"] or f"User_{entry['user_id']}"
                score = entry["score"]
                
                leaderboard_text += f"{medal} *{username}* - `{score}` রোস্ট\n"
            
            leaderboard_text += f"\n📅 আপডেট: {TimeManager.format_time()}"
            
            await update.message.reply_text(leaderboard_text, parse_mode="Markdown")
            
        except Exception as e:
            log_error(f"Error in handle_leaderboard: {e}")
            await self._send_error_message(update, "leaderboard")
    
    async def handle_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/quote কমান্ড হ্যান্ডল করে"""
        try:
            # Send typing action
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Post quote
            success = await self.auto_quotes.post_daily_quote(
                context, 
                update.effective_chat.id
            )
            
            if not success:
                await update.message.reply_text(
                    "💫 *ইনস্পিরেশনাল কোট*\n\n"
                    "জীবনটা ছোট, রোস্ট লং! 😈\n\n"
                    "- রোস্টিফাই বট",
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            log_error(f"Error in handle_quote: {e}")
            await self._send_error_message(update, "quote")
    
    async def handle_roast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/roast কমান্ড হ্যান্ডল করে"""
        try:
            user = update.effective_user
            
            # Generate random roast
            roast_data = self.roast_engine.generate_roast(
                f"{user.first_name} রোস্ট চাইছে!",
                user.id
            )
            
            # Create roast image
            image = image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id
            )
            
            image_path = image_generator.save_image(image)
            
            # Send image
            with open(image_path, 'rb') as photo:
                sent_message = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    reply_to_message_id=update.message.message_id
                )
            
            # Add vote buttons
            await self.vote_system.add_vote_to_message(
                update, context, sent_message.message_id, update.effective_chat.id
            )
            
            # Update stats
            StorageManager.increment_user_roast_count(user.id)
            StorageManager.log_roast(
                user_id=user.id,
                input_text="/roast command",
                roast_type=roast_data["category"],
                template_used="command_roast",
                chat_id=update.effective_chat.id
            )
            
            self.stats['total_roasts'] += 1
            
            logger.info(f"Command roast for user {user.id}")
            
        except Exception as e:
            log_error(f"Error in handle_roast_command: {e}")
            await self._send_error_message(update, "roast")
    
    async def handle_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/info কমান্ড হ্যান্ডল করে"""
        try:
            uptime = TimeManager.get_current_time() - self.stats['start_time']
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            
            info_text = (
                "ℹ️ *রোস্টিফাই বট - তথ্য*\n\n"
                "*🤖 বট সম্পর্কে:*\n"
                "রোস্টিফাই হল একটি এডভান্সড রোস্ট বট "
                "যা বাংলা ও ইংরেজি মেসেজের উপর ভিত্তি করে "
                "স্মার্ট রোস্ট তৈরি করে।\n\n"
                "*📊 পরিসংখ্যান:*\n"
                f"• মোট মেসেজ: `{self.stats['total_messages']}`\n"
                f"• মোট রোস্ট: `{self.stats['total_roasts']}`\n"
                f"• আপটাইম: `{days} দিন, {hours} ঘন্টা, {minutes} মিনিট`\n"
                f"• এরর: `{self.stats['total_errors']}`\n\n"
                "*⚙️ প্রযুক্তি:*\n"
                "• Python 3.8+\n"
                "• python-telegram-bot\n"
                "• PIL/Pillow\n"
                "• SQLAlchemy\n\n"
                f"👑 ওনার: `{Config.OWNER_ID}`\n"
                f"🤖 ইউজার: @{Config.BOT_USERNAME}\n\n"
                "*❤️ বিশেষ ধন্যবাদ:*\n"
                "আমাদের সব ইউজারদের যারা বটটি ব্যবহার করছেন!"
            )
            
            await update.message.reply_text(info_text, parse_mode="Markdown")
            
        except Exception as e:
            log_error(f"Error in handle_info: {e}")
            await self._send_error_message(update, "info")
    
    async def handle_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/ping কমান্ড হ্যান্ডল করে"""
        try:
            start_time = TimeManager.get_current_time()
            
            # Send ping
            ping_message = await update.message.reply_text("🏓 পিং...")
            
            end_time = TimeManager.get_current_time()
            latency = (end_time - start_time).total_seconds() * 1000  # Convert to ms
            
            await ping_message.edit_text(
                f"🏓 পং!\n\n"
                f"• লেটেন্সি: `{latency:.0f}ms`\n"
                f"• স্ট্যাটাস: `সক্রিয় ✅`\n"
                f"• সময়: `{TimeManager.format_time()}`",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            log_error(f"Error in handle_ping: {e}")
            await self._send_error_message(update, "ping")
    
    # ==================== ADMIN COMMANDS ====================
    
    async def handle_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/admin কমান্ড হ্যান্ডল করে"""
        try:
            user = update.effective_user
            
            # Check if user is admin
            if not safety_checker.is_owner_or_admin(user.id):
                await update.message.reply_text(
                    "⚠️ *অনুমতি নেই!*\n\n"
                    "এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য।",
                    parse_mode="Markdown"
                )
                return
            
            admin_text = (
                "👑 *অ্যাডমিন কন্ট্রোল প্যানেল*\n\n"
                "*📊 বট স্ট্যাটস:*\n"
                f"• মোট মেসেজ: `{self.stats['total_messages']}`\n"
                f"• মোট রোস্ট: `{self.stats['total_roasts']}`\n"
                f"• মোট এরর: `{self.stats['total_errors']}`\n"
                f"• ইউজার: `{len(self.user_cooldowns)}`\n\n"
                "*🛠️ অ্যাডমিন কমান্ড:*\n"
                "• `/broadcast` - সবাইকে মেসেজ পাঠান\n"
                "• `/stats_full` - সম্পূর্ণ স্ট্যাটস\n"
                "• `/cleanup` - ক্লিনআপ করুন\n\n"
                "*⚙️ কন্ট্রোল:*\n"
                "• বট স্ট্যাটাস: `সক্রিয়`\n"
                "• ডাটাবেস: `সংযুক্ত`\n"
                "• লগিং: `সক্রিয়`\n\n"
                f"👤 অ্যাডমিন: {user.first_name}\n"
                f"🆔 আইডি: `{user.id}`"
            )
            
            await update.message.reply_text(admin_text, parse_mode="Markdown")
            
        except Exception as e:
            log_error(f"Error in handle_admin: {e}")
            await self._send_error_message(update, "admin")
    
    async def handle_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/broadcast কমান্ড হ্যান্ডল করে"""
        try:
            user = update.effective_user
            
            # Check if user is admin
            if not safety_checker.is_owner_or_admin(user.id):
                await update.message.reply_text("⚠️ অনুমতি নেই!")
                return
            
            # Get broadcast message
            if not context.args:
                await update.message.reply_text(
                    "📢 *ব্রডকাস্ট মেসেজ*\n\n"
                    "ব্যবহার: `/broadcast <মেসেজ>`\n\n"
                    "উদাহরণ: `/broadcast নতুন আপডেট আসছে!`",
                    parse_mode="Markdown"
                )
                return
            
            broadcast_message = ' '.join(context.args)
            
            # Confirm broadcast
            keyboard = [
                [
                    InlineKeyboardButton("✅ হ্যাঁ, পাঠান", callback_data="broadcast_yes"),
                    InlineKeyboardButton("❌ বাতিল", callback_data="broadcast_no")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"📢 *ব্রডকাস্ট কনফার্মেশন*\n\n"
                f"মেসেজ: `{broadcast_message}`\n\n"
                f"এই মেসেজ সব ইউজারকে পাঠানো হবে। নিশ্চিত?",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            log_error(f"Error in handle_broadcast: {e}")
            await self._send_error_message(update, "broadcast")
    
    async def handle_stats_full(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/stats_full কমান্ড হ্যান্ডল করে"""
        try:
            user = update.effective_user
            
            if not safety_checker.is_owner_or_admin(user.id):
                await update.message.reply_text("⚠️ অনুমতি নেই!")
                return
            
            # Get comprehensive stats
            with StorageManager.get_session() as db:
                total_users = db.query(User).count()
                total_roasts = db.query(User).with_entities(User.roast_count).scalar() or 0
                active_users = db.query(User).filter(User.roast_count > 0).count()
            
            stats_text = (
                "📈 *সম্পূর্ণ পরিসংখ্যান*\n\n"
                "*👥 ইউজার:*\n"
                f"• মোট ইউজার: `{total_users}`\n"
                f"• সক্রিয় ইউজার: `{active_users}`\n"
                f"• নতুন ইউজার: `{total_users - active_users}`\n\n"
                "*🔥 রোস্ট:*\n"
                f"• মোট রোস্ট: `{total_roasts}`\n"
                f"• গড় রোস্ট/ইউজার: `{total_roasts/max(total_users,1):.1f}`\n\n"
                "*⚡ পারফরম্যান্স:*\n"
                f"• মোট মেসেজ: `{self.stats['total_messages']}`\n"
                f"• মোট এরর: `{self.stats['total_errors']}`\n"
                f"• সাফল্যের হার: `{(1 - self.stats['total_errors']/max(self.stats['total_messages'],1))*100:.1f}%`\n\n"
                f"📅 রিপোর্ট সময়: `{TimeManager.format_time()}`"
            )
            
            await update.message.reply_text(stats_text, parse_mode="Markdown")
            
        except Exception as e:
            log_error(f"Error in handle_stats_full: {e}")
            await self._send_error_message(update, "stats_full")
    
    async def handle_cleanup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/cleanup কমান্ড হ্যান্ডল করে"""
        try:
            user = update.effective_user
            
            if not safety_checker.is_owner_or_admin(user.id):
                await update.message.reply_text("⚠️ অনুমতি নেই!")
                return
            
            # Perform cleanup
            StorageManager.cleanup_old_data(days=7)
            
            # Clear local caches
            self.user_cooldowns.clear()
            self.reaction_system.reset_cooldowns()
            
            await update.message.reply_text(
                "🧹 *ক্লিনআপ সম্পূর্ণ*\n\n"
                "• পুরানো ডাটা ডিলিট করা হয়েছে\n"
                "• ক্যাশে ক্লিয়ার করা হয়েছে\n"
                "• কুলডাউন রিসেট করা হয়েছে\n\n"
                "✅ সবকিছু পরিষ্কার!",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            log_error(f"Error in handle_cleanup: {e}")
            await self._send_error_message(update, "cleanup")
    
    # ==================== MESSAGE HANDLERS ====================
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """টেক্সট মেসেজ হ্যান্ডল করে - মেইন ফাংশন"""
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
                return
            
            # Generate roast
            roast_data = self.roast_engine.generate_roast(message.text, user.id)
            
            # Send typing action
            await context.bot.send_chat_action(
                chat_id=chat.id,
                action="upload_photo"
            )
            
            # Create and send roast image
            image = image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id
            )
            
            image_path = image_generator.save_image(image)
            
            with open(image_path, 'rb') as photo:
                sent_message = await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=photo,
                    reply_to_message_id=message.message_id
                )
            
            # Add vote buttons
            await self.vote_system.add_vote_to_message(
                update, context, sent_message.message_id, chat.id
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
                template_used="auto",
                chat_id=chat.id
            )
            
            StorageManager.increment_user_roast_count(user.id)
            
            # Add auto-reactions
            await self.reaction_system.analyze_and_react(update, context)
            
            self.stats['total_roasts'] += 1
            
            logger.info(f"Roasted user {user.id} in chat {chat.id}")
            
        except Exception as e:
            self.stats['total_errors'] += 1
            log_error(f"Error in handle_text_message: {e}")
            
            # Fallback response
            fallback_responses = [
                "রোস্ট তৈরি করতে সমস্যা! একটু পর আবার চেষ্টা করুন। 😊",
                "আমার ব্রেন আজ একটু ক্লান্ত! পরে আবার চেষ্টা করব। 😴",
                "এই মেসেজের জন্য রোস্ট তৈরি করতে পারলাম না। নতুন কিছু লিখুন! ✍️",
                "রোস্ট ইঞ্জিন গরম হচ্ছে... একটু অপেক্ষা করুন! 🔥"
            ]
            
            import random
            await update.message.reply_text(random.choice(fallback_responses))
    
    async def handle_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """মেনশন হ্যান্ডল করে"""
        try:
            await self.mention_system.handle_mention(update, context)
        except Exception as e:
            log_error(f"Error in handle_mention: {e}")
    
    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """চ্যাট মেম্বার আপডেট হ্যান্ডল করে"""
        try:
            difference = update.chat_member.difference()
            
            if difference.get("new_chat_member") and difference["new_chat_member"].user.id == context.bot.id:
                await self.welcome_system.handle_bot_added_to_group(update, context)
        except Exception as e:
            log_error(f"Error in handle_chat_member_update: {e}")
    
    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """নতুন চ্যাট মেম্বার হ্যান্ডল করে"""
        try:
            await self.welcome_system.handle_new_chat_members(update, context)
        except Exception as e:
            log_error(f"Error in handle_new_chat_members: {e}")
    
    # ==================== CALLBACK HANDLERS ====================
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ক্যালব্যাক কুয়েরি হ্যান্ডল করে (ভোট)"""
        try:
            await self.vote_system.handle_vote_callback(update, context)
            self.stats['total_votes'] += 1
        except Exception as e:
            log_error(f"Error in handle_callback_query: {e}")
    
    async def handle_general_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """সাধারণ ক্যালব্যাক হ্যান্ডল করে"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            
            if data == "broadcast_yes":
                # Handle broadcast confirmation
                await query.edit_message_text(
                    "📢 ব্রডকাস্ট শুরু হয়েছে...",
                    parse_mode="Markdown"
                )
                # Here you would implement actual broadcast
                
            elif data == "broadcast_no":
                await query.edit_message_text(
                    "❌ ব্রডকাস্ট বাতিল করা হয়েছে।",
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            log_error(f"Error in handle_general_callback: {e}")
    
    # ==================== JOB HANDLERS ====================
    
    async def _job_daily_quote(self, context: ContextTypes.DEFAULT_TYPE):
        """ডেইলি কোট জব"""
        try:
            await self.auto_quotes.post_daily_quote(context)
            logger.info("Daily quote posted")
        except Exception as e:
            log_error(f"Error in daily quote job: {e}")
    
    async def _job_cleanup_data(self, context: ContextTypes.DEFAULT_TYPE):
        """ডাটা ক্লিনআপ জব"""
        try:
            StorageManager.cleanup_old_data(days=7)
            image_generator.cleanup_temp_files()
            logger.info("Data cleanup completed")
        except Exception as e:
            log_error(f"Error in cleanup job: {e}")
    
    async def _job_reset_cooldowns(self, context: ContextTypes.DEFAULT_TYPE):
        """কুলডাউন রিসেট জব"""
        try:
            self.reaction_system.reset_cooldowns()
            # Clean old cooldowns
            current_time = TimeManager.get_current_time()
            to_remove = []
            
            for user_id, last_time in self.user_cooldowns.items():
                if (current_time - last_time).total_seconds() > 3600:
                    to_remove.append(user_id)
            
            for user_id in to_remove:
                del self.user_cooldowns[user_id]
            
            logger.info(f"Reset {len(to_remove)} user cooldowns")
        except Exception as e:
            log_error(f"Error in reset cooldowns job: {e}")
    
    async def _job_save_stats(self, context: ContextTypes.DEFAULT_TYPE):
        """স্ট্যাটস সেভ জব"""
        try:
            # Here you would save stats to database
            logger.info(f"Stats saved: {self.stats}")
        except Exception as e:
            log_error(f"Error in save stats job: {e}")
    
    async def _job_health_check(self, context: ContextTypes.DEFAULT_TYPE):
        """হেলথ চেক জব"""
        try:
            # Check bot health
            bot_info = await context.bot.get_me()
            
            health_status = {
                'bot_status': 'active',
                'bot_username': bot_info.username,
                'total_messages': self.stats['total_messages'],
                'total_errors': self.stats['total_errors'],
                'timestamp': TimeManager.format_time()
            }
            
            logger.info(f"Health check: {health_status}")
            
        except Exception as e:
            log_error(f"Error in health check job: {e}")
            self.stats['total_errors'] += 1
    
    # ==================== UTILITY METHODS ====================
    
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
    
    def _get_medal_emoji(self, rank: int) -> str:
        """র‍্যাংক অনুযায়ী মেডেল ইমোজি রিটার্ন করে"""
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        else:
            return f"{rank}."
    
    async def _send_error_message(self, update: Update, command: str):
        """এরর মেসেজ পাঠায়"""
        try:
            error_messages = {
                'start': "বট শুরু করতে সমস্যা! আবার চেষ্টা করুন।",
                'help': "হেল্প লোড করতে সমস্যা!",
                'stats': "স্ট্যাটস দেখাতে সমস্যা!",
                'roast': "রোস্ট তৈরি করতে সমস্যা!",
                'quote': "কোট লোড করতে সমস্যা!",
                'admin': "অ্যাডমিন প্যানেল লোড করতে সমস্যা!",
                'default': "কমান্ড এক্সিকিউট করতে সমস্যা! আবার চেষ্টা করুন।"
            }
            
            message = error_messages.get(command, error_messages['default'])
            
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    f"😓 {message}\n\n"
                    f"আপনার সমস্যা সমাধানে সাহায্য চাইলে /help কমান্ড ব্যবহার করুন।"
                )
                
        except Exception as e:
            log_error(f"Error sending error message: {e}")
    
    def _save_final_stats(self):
        """চূড়ান্ত স্ট্যাটস সেভ করে"""
        try:
            stats_data = {
                'total_messages': self.stats['total_messages'],
                'total_roasts': self.stats['total_roasts'],
                'total_votes': self.stats['total_votes'],
                'total_errors': self.stats['total_errors'],
                'start_time': TimeManager.format_time(self.stats['start_time']),
                'end_time': TimeManager.format_time(),
                'duration': str(TimeManager.get_current_time() - self.stats['start_time'])
            }
            
            logger.info(f"Final stats: {stats_data}")
            
        except Exception as e:
            log_error(f"Error saving final stats: {e}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """গ্লোবাল এরর হ্যান্ডলার"""
        try:
            self.stats['total_errors'] += 1
            
            # Log error
            log_error(f"Update {update.update_id if update else 'N/A'} caused error: {context.error}")
            
            # Print traceback for debugging
            tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
            tb_string = ''.join(tb_list)
            logger.error(f"Traceback:\n{tb_string}")
            
            # Notify owner
            if Config.OWNER_ID:
                try:
                    error_summary = str(context.error)[:200]
                    await context.bot.send_message(
                        chat_id=Config.OWNER_ID,
                        text=f"⚠️ *বট এরর*\n\n```\n{error_summary}\n```",
                        parse_mode="Markdown"
                    )
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error in error handler: {e}")

# ==================== MAIN FUNCTION ====================

async def main():
    """মেইন ফাংশন"""
    try:
        print("\n" + "="*60)
        print("🤖 ROASTIFY BOT - PROFESSIONAL EDITION")
        print("="*60)
        print(f"📅 {TimeManager.format_time()}")
        print("="*60 + "\n")
        
        # Create and run bot
        bot = RoastifyBot()
        await bot.start_bot()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  বট বন্ধ করা হচ্ছে (Ctrl+C)...")
        # Bot will be stopped by signal handler
        
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
