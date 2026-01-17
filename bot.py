import asyncio
from pathlib import Path
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    ChatMemberHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
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
        Config.validate()
        self.roast_engine = RoastEngine()
        self.safety_checker = SafetyChecker()
        self.image_generator = ImageGenerator()
        self.welcome_system = WelcomeSystem()
        self.vote_system = VoteSystem()
        self.mention_system = MentionSystem()
        self.reaction_system = ReactionSystem()
        self.admin_protection = AdminProtection()
        self.auto_quotes = AutoQuoteSystem()

        init_database()
        self.application = None
        self.user_cooldowns = {}
        logger.info("RoastifyBot initialized")

    def _register_handlers(self):
        """সকল হ্যান্ডলার রেজিস্টার করে"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("stats", self.handle_stats))
        self.application.add_handler(CommandHandler("leaderboard", self.handle_leaderboard))
        self.application.add_handler(CommandHandler("quote", self.handle_quote))
        self.application.add_handler(CommandHandler("admin", self.handle_admin))
        self.application.add_handler(CommandHandler("protect_stats", self.handle_protect_stats))
        self.application.add_handler(CommandHandler("reset_cooldowns", self.handle_reset_cooldowns))

        # Message handlers
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_text_message
        ))
        self.application.add_handler(MessageHandler(
            filters.TEXT & filters.Entity("mention"),
            self.handle_mention
        ))
        self.application.add_handler(ChatMemberHandler(
            self.handle_chat_member_update,
            ChatMemberHandler.CHAT_MEMBER
        ))
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            self.handle_new_chat_members
        ))

        # Vote callback handlers
        self.application.add_handler(CallbackQueryHandler(
            self.vote_system.handle_vote_callback,
            pattern="^vote_"
        ))

        # Error handler
        self.application.add_error_handler(self.error_handler)
        logger.info("All handlers registered")

    def _register_jobs(self):
        """জব/সিডিউলার রেজিস্টার করে"""
        job_queue = self.application.job_queue

        # Daily quote at 12:00 PM
        job_queue.run_daily(
            self._post_daily_quote_job,
            time=TimeManager.get_current_time().replace(hour=12, minute=0, second=0),
            days=(0, 1, 2, 3, 4, 5, 6),
            name="daily_quote"
        )

        # Cleanup old data at 3:00 AM
        job_queue.run_daily(
            self._cleanup_data_job,
            time=TimeManager.get_current_time().replace(hour=3, minute=0, second=0),
            days=(0, 1, 2, 3, 4, 5, 6),
            name="cleanup_data"
        )

        # Reset reaction cooldowns hourly
        job_queue.run_repeating(
            self._reset_cooldowns_job,
            interval=3600,
            first=10,
            name="reset_cooldowns"
        )

        logger.info("Jobs scheduled")

    async def _post_daily_quote_job(self, context: ContextTypes.DEFAULT_TYPE):
        """ডেইলি কোট জব"""
        await self.auto_quotes.post_daily_quote(context)

    async def _cleanup_data_job(self, context: ContextTypes.DEFAULT_TYPE):
        """ডাটা ক্লিনআপ জব"""
        StorageManager.cleanup_old_data(days=30)

    async def _reset_cooldowns_job(self, context: ContextTypes.DEFAULT_TYPE):
        """কুলডাউন রিসেট জব"""
        self.reaction_system.reset_cooldowns()

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

    def run(self):
        """বট চালু করে"""
        try:
            # Create application
            self.application = ApplicationBuilder().token(Config.BOT_TOKEN).build()
            
            # Setup handlers and jobs
            self._register_handlers()
            self._register_jobs()
            
            # Run the bot
            logger.info("Starting RoastifyBot...")
            
            # Import event loop
            import asyncio
            
            # Get event loop and run
            loop = asyncio.get_event_loop()
            
            # Set bot commands
            loop.run_until_complete(self._set_bot_commands())
            
            # Start polling
            self.application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

    # ========== ASYNC COMMAND HANDLERS ==========

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """বট শুরু করতে"""
        await self.welcome_system.handle_bot_start(update, context)

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """সাহায্য দেখায়"""
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
            "• বট ওনার/অ্যাডমিনকে রেসপেক্ট করুন\n\n"
            f"বট: @{Config.BOT_USERNAME}"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ইউজার স্ট্যাটস দেখায়"""
        user = update.effective_user
        
        # Get user from database
        with StorageManager.get_session() as db:
            from database.models import User
            user_record = db.query(User).filter(User.user_id == user.id).first()
            
            if user_record:
                stats_text = (
                    f"📊 *{user.first_name}'র স্ট্যাটস*\n\n"
                    f"• মোট রোস্ট: {user_record.roast_count}\n"
                    f"• মোট ভোট: {user_record.vote_count}\n"
                    f"• রিএকশন: {user_record.reaction_count}\n"
                    f"• যোগদান: {TimeManager.format_time(user_record.created_at)}\n"
                )
            else:
                stats_text = "📊 *স্ট্যাটস পাওয়া যায়নি*\n\nআপনি এখনো কোনো রোস্ট পাননি!"
        
        await update.message.reply_text(stats_text, parse_mode="Markdown")

    async def handle_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """লিডারবোর্ড দেখায়"""
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
        
        leaderboard_text += "\nরোস্ট খেতে চাইলে শুধু মেসেজ লিখুন! 😈"
        
        await update.message.reply_text(leaderboard_text, parse_mode="Markdown")

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

    async def handle_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """র‍্যান্ডম কোট পাঠায়"""
        await self.auto_quotes.post_daily_quote(context, update.effective_chat.id)

    async def handle_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """অ্যাডমিন প্যানেল দেখায়"""
        user = update.effective_user
        
        if not self.safety_checker.is_owner_or_admin(user.id):
            await update.message.reply_text("⚠️ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য!")
            return
        
        admin_text = (
            "👑 *অ্যাডমিন প্যানেল*\n\n"
            "*কমান্ডস:*\n"
            "/protect_stats - প্রটেকশন স্ট্যাটস\n"
            "/reset_cooldowns - সব কুলডাউন রিসেট\n\n"
            "*বট ইনফো:*\n"
            f"ইউজার: @{Config.BOT_USERNAME}\n"
            f"ওনার: {Config.OWNER_ID}\n"
            f"ইউজার ID: {user.id}\n"
            f"চ্যাট ID: {update.effective_chat.id if update.effective_chat else 'N/A'}"
        )
        
        await update.message.reply_text(admin_text, parse_mode="Markdown")

    async def handle_protect_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """প্রটেকশন স্ট্যাটস দেখায়"""
        await self.admin_protection.handle_admin_command(update, context, "protect_stats")

    async def handle_reset_cooldowns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """কুলডাউন রিসেট করে"""
        await self.admin_protection.handle_admin_command(update, context, "reset_cooldowns")

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """সাধারণ টেক্সট মেসেজ হ্যান্ডল করে"""
        message = update.effective_message
        user = update.effective_user
        chat = update.effective_chat
        
        if not message.text:
            return
        
        # 1. Check admin protection
        if await self.admin_protection.check_and_protect(update, context):
            return
        
        # 2. Check for mentions
        if await self.mention_system.handle_mention(update, context):
            return
        
        # 3. Validate input
        if not self._validate_user_input(message.text, user.id, chat.id):
            return
        
        # 4. Generate roast
        roast_data = self.roast_engine.generate_roast(message.text, user.id)
        
        # 5. Create roast image
        try:
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id
            )
            
            # Save image
            image_path = self.image_generator.save_image(
                image, 
                f"roast_{user.id}_{chat.id}.png"
            )
            
            # Send image
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
            
            # Log roast
            StorageManager.log_roast(
                user_id=user.id,
                input_text=message.text[:200],
                roast_type=roast_data["category"],
                template_used="auto_generated",
                chat_id=chat.id
            )
            
            # Increment user roast count
            StorageManager.increment_user_roast_count(user.id)
            
            # Add auto-reactions
            await self.reaction_system.analyze_and_react(update, context)
            
            logger.info(f"Roasted user {user.id} in chat {chat.id}")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await message.reply_text("😓 ইমেজ তৈরি করতে সমস্যা! আবার চেষ্টা করুন।")

    def _validate_user_input(self, text: str, user_id: int, chat_id: int) -> bool:
        """ইউজার ইনপুট ভ্যালিডেট করে"""
        # Check minimum length
        if len(text) < Config.MIN_INPUT_LENGTH:
            return False
        
        # Check safety
        if not self.safety_checker.is_safe_content(text):
            return False
        
        # Check for disallowed content
        if self.safety_checker.contains_disallowed_content(text):
            return False
        
        return True

    async def handle_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """মেনশন হ্যান্ডল করে"""
        await self.mention_system.handle_mention(update, context)

    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """চ্যাট মেম্বার আপডেট হ্যান্ডল করে"""
        # Handle bot being added to groups
        difference = update.chat_member.difference()
        
        if difference.get("new_chat_member") and difference["new_chat_member"].user.id == context.bot.id:
            # Bot was added to group
            await self.welcome_system.handle_bot_added_to_group(update, context)

    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """নতুন চ্যাট মেম্বার হ্যান্ডল করে"""
        await self.welcome_system.handle_new_chat_members(update, context)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """এরর হ্যান্ডল করে"""
        logger.error(f"Update error: {context.error}")
        
        # Notify owner about critical errors
        if Config.OWNER_ID:
            try:
                error_msg = f"⚠️ *বট এরর*\n\n{str(context.error)[:200]}..."
                await context.bot.send_message(
                    chat_id=Config.OWNER_ID,
                    text=error_msg,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Error notifying owner: {e}")

# Simple runner function
def main():
    """মেইন রানার ফাংশন"""
    bot = RoastifyBot()
    bot.run()

if __name__ == "__main__":
    main()
