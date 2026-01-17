import asyncio
from typing import Dict, List, Optional
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters
)
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager
from database.storage import StorageManager
from database.models import init_database
from roast_engine.roaster import RoastEngine
from roast_engine.safety_check import SafetyChecker
from image_engine.image_generator import ImageGenerator
from features.welcome_system import WelcomeSystem
from features.vote_system import VoteSystem
from features.mention_system import MentionSystem
from features.reaction_system import ReactionSystem
from features.admin_protection import AdminProtection
from features.auto_quotes import AutoQuoteSystem

class RoastifyBot:
    def __init__(self):
        # Initialize config
        Config.validate()
        
        # Initialize components
        self.roast_engine = RoastEngine()
        self.safety_checker = SafetyChecker()
        self.image_generator = ImageGenerator()
        
        # Initialize features
        self.welcome_system = WelcomeSystem()
        self.vote_system = VoteSystem()
        self.mention_system = MentionSystem()
        self.reaction_system = ReactionSystem()
        self.admin_protection = AdminProtection()
        self.auto_quotes = AutoQuoteSystem()
        
        # Initialize database
        init_database()
        
        # Application instance
        self.application = None
        
        # User cooldowns
        self.user_cooldowns = {}
        
        logger.info("RoastifyBot initialized")
    
    async def start(self):
        """বট শুরু করে"""
        try:
            # Create application
            self.application = Application.builder().token(Config.BOT_TOKEN).build()
            
            # Register handlers
            self._register_handlers()
            
            # Register jobs
            self._register_jobs()
            
            # Set bot commands
            await self._set_bot_commands()
            
            # Start the bot
            logger.info("Starting RoastifyBot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("✅ RoastifyBot is now running!")
            
            # Keep running
            await self._keep_alive()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
    
    def _register_handlers(self):
        """সকল হ্যান্ডলার রেজিস্টার করে"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("stats", self.handle_stats))
        self.application.add_handler(CommandHandler("leaderboard", self.handle_leaderboard))
        self.application.add_handler(CommandHandler("quote", self.handle_quote))
        
        # Admin commands
        self.application.add_handler(CommandHandler("admin", self.handle_admin))
        self.application.add_handler(CommandHandler("protect_stats", self.handle_protect_stats))
        self.application.add_handler(CommandHandler("reset_cooldowns", self.handle_reset_cooldowns))
        
        # Message handlers
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_text_message
        ))
        
        # Mention handler (when bot is mentioned)
        self.application.add_handler(MessageHandler(
            filters.TEXT & filters.Entity("mention"),
            self.handle_mention
        ))
        
        # New chat members handler
        self.application.add_handler(ChatMemberHandler(
            self.handle_chat_member_update,
            ChatMemberHandler.CHAT_MEMBER
        ))
        
        # New chat members (alternative)
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            self.handle_new_chat_members
        ))
        
        # Callback query handlers (for votes)
        self.application.add_handler(self.vote_system.get_callback_handler())
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
        logger.info("All handlers registered")
    
    def _register_jobs(self):
        """জব/সিডিউলার রেজিস্টার করে"""
        job_queue = self.application.job_queue
        
        # Daily quote at 12:00 PM
        job_queue.run_daily(
            self._post_daily_quotes,
            time=TimeManager.get_current_time().replace(hour=12, minute=0, second=0),
            days=(0, 1, 2, 3, 4, 5, 6),
            name="daily_quote"
        )
        
        # Cleanup old data every day at 3 AM
        job_queue.run_daily(
            self._cleanup_old_data,
            time=TimeManager.get_current_time().replace(hour=3, minute=0, second=0),
            days=(0, 1, 2, 3, 4, 5, 6),
            name="cleanup_data"
        )
        
        # Reset reaction cooldowns hourly
        job_queue.run_repeating(
            self._reset_reaction_cooldowns,
            interval=3600,  # 1 hour
            first=10,
            name="reset_cooldowns"
        )
        
        logger.info("Jobs scheduled")
    
    async def _set_bot_commands(self):
        """বট কমান্ড সেট করে"""
        commands = [
            BotCommand("start", "বট শুরু করুন"),
            BotCommand("help", "সাহায্য পান"),
            BotCommand("stats", "আপনার স্ট্যাটস দেখুন"),
            BotCommand("leaderboard", "লিডারবোর্ড দেখুন"),
            BotCommand("quote", "র‍্যান্ডম কোট পান"),
        ]
        
        await self.application.bot.set_my_commands(commands)
        logger.info("Bot commands set")
    
    # ========== COMMAND HANDLERS ==========
    
    async def handle_start(self, update: Update, context):
        """/start কমান্ড হ্যান্ডল করে"""
        await self.welcome_system.handle_bot_start(update, context)
    
    async def handle_help(self, update: Update, context):
        """/help কমান্ড হ্যান্ডল করে"""
        help_text = (
            "🤖 *Roastify Bot Help*\n\n"
            "*কীভাবে ব্যবহার করবেন:*\n"
            "• শুধু মেসেজ লিখুন, রোস্ট ইমেজ পাবেন\n"
            "• গ্রুপে কাউকে মেনশন করুন রোস্টের জন্য\n"
            "• ভোট দিয়ে রেটিং দিন\n\n"
            "*কমান্ডস:*\n"
            "/start - বট শুরু করুন\n"
            "/stats - আপনার স্ট্যাটস\n"
            "/leaderboard - টপ রোস্টেড ইউজার\n"
            "/quote - র‍্যান্ডম কোট\n\n"
            "*নিয়ম:*\n"
            "• অপমানজনক ভাষা ব্যবহার করবেন না\n"
            "• বট ওনার/অ্যাডমিনকে রেসপেক্ট করুন\n"
            "• মজা করুন, কিন্তু সীমার মধ্যে থাকুন!\n\n"
            f"বট: @{Config.BOT_USERNAME}"
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def handle_stats(self, update: Update, context):
        """/stats কমান্ড হ্যান্ডল করে"""
        user = update.effective_user
        
        # Get user stats from database
        with StorageManager.get_session() as db:
            user_record = db.query(User).filter(User.user_id == user.id).first()
            
            if user_record:
                stats_text = (
                    f"📊 *{user.first_name}'র স্ট্যাটস*\n\n"
                    f"• মোট রোস্ট: {user_record.roast_count}\n"
                    f"• মোট ভোট: {user_record.vote_count}\n"
                    f"• রিএকশন: {user_record.reaction_count}\n"
                    f"• যোগদান: {TimeManager.format_time(user_record.created_at)}\n\n"
                    f"র‍্যাংক: #{self._get_user_rank(user.id)}"
                )
            else:
                stats_text = "📊 *স্ট্যাটস পাওয়া যায়নি*\n\nআপনি এখনো কোনো রোস্ট পাননি!"
        
        await update.message.reply_text(stats_text, parse_mode="Markdown")
    
    async def handle_leaderboard(self, update: Update, context):
        """/leaderboard কমান্ড হ্যান্ডল করে"""
        leaderboard = StorageManager.get_leaderboard("most_roasted", limit=10)
        
        if not leaderboard:
            await update.message.reply_text("📊 *লিডারবোর্ড খালি*\n\nএখনো কোনো ডাটা নেই!")
            return
        
        leaderboard_text = "🏆 *টপ রোস্টেড ইউজার*\n\n"
        
        for entry in leaderboard:
            medal = self._get_medal(entry["rank"])
            username = entry["username"]
            score = entry["score"]
            
            leaderboard_text += f"{medal} *{username}* - {score} রোস্ট\n"
        
        leaderboard_text += f"\nআপনার র‍্যাংক: #{self._get_user_rank(update.effective_user.id)}"
        
        await update.message.reply_text(leaderboard_text, parse_mode="Markdown")
    
    async def handle_quote(self, update: Update, context):
        """/quote কমান্ড হ্যান্ডল করে"""
        await self.auto_quotes.post_daily_quote(context, update.effective_chat.id)
    
    async def handle_admin(self, update: Update, context):
        """/admin কমান্ড হ্যান্ডল করে"""
        user = update.effective_user
        
        if not self.safety_checker.is_owner_or_admin(user.id):
            await update.message.reply_text("⚠️ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য!")
            return
        
        admin_text = (
            "👑 *অ্যাডমিন প্যানেল*\n\n"
            "*কমান্ডস:*\n"
            "/protect_stats - প্রটেকশন স্ট্যাটস\n"
            "/reset_cooldowns - সব কুলডাউন রিসেট\n"
            "/broadcast - ব্রডকাস্ট মেসেজ\n\n"
            "*বট ইনফো:*\n"
            f"ইউজার: @{Config.BOT_USERNAME}\n"
            f"ওনার: {Config.OWNER_ID}\n"
            f"চ্যাট: {update.effective_chat.id if update.effective_chat else 'N/A'}"
        )
        
        await update.message.reply_text(admin_text, parse_mode="Markdown")
    
    async def handle_protect_stats(self, update: Update, context):
        """/protect_stats কমান্ড হ্যান্ডল করে"""
        await self.admin_protection.handle_admin_command(update, context, "protect_stats")
    
    async def handle_reset_cooldowns(self, update: Update, context):
        """/reset_cooldowns কমান্ড হ্যান্ডল করে"""
        await self.admin_protection.handle_admin_command(update, context, "reset_cooldowns")
    
    # ========== MESSAGE HANDLERS ==========
    
    async def handle_text_message(self, update: Update, context):
        """সাধারণ টেক্সট মেসেজ হ্যান্ডল করে"""
        message = update.effective_message
        user = update.effective_user
        chat = update.effective_chat
        
        if not message.text:
            return
        
        # 1. First check admin protection
        if await self.admin_protection.check_and_protect(update, context):
            return
        
        # 2. Check for mentions (if not already handled)
        if await self.mention_system.handle_mention(update, context):
            return
        
        # 3. Validate input
        if not self._validate_user_input(message.text, user.id, chat.id):
            return
        
        # 4. Generate roast
        roast_data = self.roast_engine.generate_roast(message.text, user.id)
        
        # 5. Check if user photo should be used
        use_photo = False
        photo_path = None
        
        if self._should_use_user_photo(message.text, roast_data["category"]):
            photo_path = await self._get_user_photo(context, user.id, chat.id)
            use_photo = photo_path is not None
        
        # 6. Create roast image
        try:
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id,
                user_photo_path=photo_path if use_photo else None
            )
            
            image_path = self.image_generator.save_image(
                image, 
                f"roast_{user.id}_{chat.id}.png"
            )
            
            # 7. Send image
            with open(image_path, 'rb') as photo:
                sent_message = await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=photo,
                    reply_to_message_id=message.message_id
                )
            
            # 8. Add vote buttons
            await self.vote_system.add_vote_to_message(
                update, context, sent_message.message_id, chat.id
            )
            
            # 9. Log roast
            StorageManager.log_roast(
                user_id=user.id,
                input_text=message.text[:200],
                roast_type=roast_data["category"],
                template_used="auto_generated",
                chat_id=chat.id
            )
            
            # 10. Increment user roast count
            StorageManager.increment_user_roast_count(user.id)
            
            # 11. Add auto-reactions
            await self.reaction_system.analyze_and_react(update, context)
            
            logger.info(f"Roasted user {user.id} in chat {chat.id}")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await message.reply_text("😓 ইমেজ তৈরি করতে সমস্যা! আবার চেষ্টা করুন।")
    
    async def handle_mention(self, update: Update, context):
        """মেনশন হ্যান্ডল করে"""
        await self.mention_system.handle_mention(update, context)
    
    async def handle_chat_member_update(self, update: Update, context):
        """চ্যাট মেম্বার আপডেট হ্যান্ডল করে"""
        # This handles bot being added/removed from groups
        difference = update.chat_member.difference()
        
        if difference.get("new_chat_member") and difference["new_chat_member"].user.id == context.bot.id:
            # Bot was added to group
            await self.welcome_system.handle_bot_added_to_group(update, context)
    
    async def handle_new_chat_members(self, update: Update, context):
        """নতুন চ্যাট মেম্বার হ্যান্ডল করে"""
        await self.welcome_system.handle_new_chat_members(update, context)
    
    # ========== JOB HANDLERS ==========
    
    async def _post_daily_quotes(self, context):
        """ডেইলি কোট পোস্ট করে"""
        logger.info("Posting daily quotes...")
        
        # Get all active chats from database
        with StorageManager.get_session() as db:
            chats = db.query(Chat).filter(Chat.roast_enabled == True).all()
        
        for chat in chats:
            if self.auto_quotes.should_post_daily_quote(chat.chat_id):
                await self.auto_quotes.post_daily_quote(context, chat.chat_id)
    
    async def _cleanup_old_data(self, context):
        """পুরানো ডাটা ক্লিনআপ করে"""
        logger.info("Cleaning up old data...")
        StorageManager.cleanup_old_data(days=30)
    
    async def _reset_reaction_cooldowns(self, context):
        """রিএকশন কুলডাউন রিসেট করে"""
        self.reaction_system.reset_cooldowns()
    
    # ========== UTILITY METHODS ==========
    
    def _validate_user_input(self, text: str, user_id: int, chat_id: int) -> bool:
        """ইউজার ইনপুট ভ্যালিডেট করে"""
        # Check cooldown
        if not self._check_user_cooldown(user_id, chat_id):
            return False
        
        # Check safety
        if not self.safety_checker.is_safe_content(text):
            return False
        
        # Check minimum length
        if len(text) < Config.MIN_INPUT_LENGTH:
            return False
        
        # Check for disallowed content
        if self.safety_checker.contains_disallowed_content(text):
            return False
        
        return True
    
    def _check_user_cooldown(self, user_id: int, chat_id: int) -> bool:
        """ইউজার কুলডাউন চেক করে"""
        key = f"{user_id}_{chat_id}"
        
        if key in self.user_cooldowns:
            last_time = self.user_cooldowns[key]
            time_diff = (TimeManager.get_current_time() - last_time).total_seconds()
            
            if time_diff < 5:  # 5 seconds cooldown
                return False
        
        self.user_cooldowns[key] = TimeManager.get_current_time()
        return True
    
    def _should_use_user_photo(self, text: str, category: str) -> bool:
        """ইউজার ফটো ইউজ করা উচিত কিনা"""
        from roast_engine.categories import RoastCategoryManager
        return RoastCategoryManager.should_use_profile_photo(text, category)
    
    async def _get_user_photo(self, context, user_id: int, chat_id: int) -> Optional[str]:
        """ইউজারের প্রোফাইল ফটো ডাউনলোড করে"""
        try:
            photos = await context.bot.get_user_profile_photos(user_id, limit=1)
            
            if photos.total_count > 0:
                photo = photos.photos[0][-1]  # Get highest quality
                file = await context.bot.get_file(photo.file_id)
                
                # Save locally
                import os
                photo_path = f"temp/user_{user_id}_photo.jpg"
                await file.download_to_drive(photo_path)
                
                return photo_path
        except Exception as e:
            logger.error(f"Error getting user photo: {e}")
        
        return None
    
    def _get_user_rank(self, user_id: int) -> int:
        """ইউজারের র‍্যাংক রিটার্ন করে"""
        # Simplified implementation
        return 999
    
    def _get_medal(self, rank: int) -> str:
        """র‍্যাংক অনুযায়ী মেডেল রিটার্ন করে"""
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        else:
            return f"{rank}."
    
    async def _keep_alive(self):
        """বট চলমান রাখে"""
        while True:
            try:
                await asyncio.sleep(3600)  # Sleep for 1 hour
                logger.debug("Bot is still running...")
            except KeyboardInterrupt:
                logger.info("Shutting down bot...")
                await self.stop()
                break
    
    async def stop(self):
        """বট বন্ধ করে"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
        logger.info("Bot stopped")
    
    async def error_handler(self, update: Update, context):
        """এরর হ্যান্ডল করে"""
        logger.error(f"Exception while handling update: {context.error}")
        
        # Notify owner about critical errors
        if Config.OWNER_ID:
            try:
                error_msg = f"⚠️ *বট এরর*\n\n{str(context.error)[:200]}..."
                await context.bot.send_message(
                    chat_id=Config.OWNER_ID,
                    text=error_msg,
                    parse_mode="Markdown"
                )
            except:
                pass