#!/usr/bin/env python3
"""
🤖 Roastify Telegram Bot - Dynamic Module Loading Version
✅ Auto-load modules from master_modules.py
"""

import os
import sys
import asyncio
import random
import traceback
import importlib
from datetime import datetime
from typing import Dict, List, Optional, Any

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
    ContextTypes,
    filters
)
from telegram.constants import ParseMode, ChatAction

# Import configuration
from config import Config

# Import master module registry
from master_modules import MODULE_REGISTRY, MODULE_CATEGORIES, MODULE_DEPENDENCIES


class DynamicModuleLoader:
    """ডাইনামিক মডিউল লোডার - মাস্টার ফাইল থেকে সব লোড করবে"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.modules = {}
        self.logger = None
        
    def load_all_modules(self):
        """সব মডিউল লোড করুন"""
        print("🔄 Loading modules from master_modules.py...")
        
        # First load core modules
        for module_name in MODULE_CATEGORIES.get("core", []):
            self.load_module(module_name)
        
        # Then load other modules
        for category in ["roast", "image", "features"]:
            for module_name in MODULE_CATEGORIES.get(category, []):
                self.load_module(module_name)
        
        print(f"✅ Loaded {len(self.modules)} modules successfully")
        return self.modules
    
    def load_module(self, module_name):
        """একটি মডিউল লোড করুন"""
        try:
            if module_name in self.modules:
                return self.modules[module_name]
            
            module_info = MODULE_REGISTRY.get(module_name)
            if not module_info:
                print(f"⚠️ Module {module_name} not found in registry")
                return None
            
            # Check dependencies
            deps = MODULE_DEPENDENCIES.get(module_name, [])
            for dep in deps:
                if dep not in self.modules:
                    print(f"⚠️ Loading dependency {dep} for {module_name}")
                    self.load_module(dep)
            
            # Import module
            module = importlib.import_module(f"modules.{module_name}")
            
            # Get class
            class_name = module_info["class"]
            module_class = getattr(module, class_name)
            
            # Create instance with appropriate parameters
            instance_params = module_info.get("params", [])
            if instance_params:
                # Pass required parameters
                params = []
                for param in instance_params:
                    if param == "bot":
                        params.append(self.bot)
                    elif param in self.modules:
                        params.append(self.modules[param])
                    else:
                        params.append(None)
                
                instance = module_class(*params)
            elif "factory" in module_info:
                # Use factory function
                factory_func = getattr(module, module_info["factory"])
                instance = factory_func()
            else:
                # Default constructor
                instance = module_class()
            
            # Store instance
            instance_name = module_info["instance_name"]
            self.modules[instance_name] = instance
            
            # Set logger if this is the logger module
            if module_name == "logger":
                self.logger = instance
                self.bot.logger = instance
            
            print(f"✅ Loaded: {module_name} -> {instance_name}")
            return instance
            
        except Exception as e:
            print(f"❌ Failed to load module {module_name}: {e}")
            traceback.print_exc()
            return None
    
    def get_module(self, module_name):
        """মডিউল ইনস্ট্যান্স পাওয়া"""
        return self.modules.get(module_name)


class RoastifyBot:
    """রোস্টিফাই বট - ডাইনামিক মডিউল লোডিং ভার্সন"""
    
    def __init__(self):
        """বট ইনিশিয়ালাইজেশন"""
        try:
            # Validate configuration
            if hasattr(Config, 'validate'):
                Config.validate()
            
            # Initialize dynamic module loader
            self.module_loader = DynamicModuleLoader(self)
            
            # Load all modules
            self.modules = self.module_loader.load_all_modules()
            
            # Set up shortcuts for commonly used modules
            self._setup_module_shortcuts()
            
            # Bot state
            self.application = None
            self.is_running = False
            self.user_cooldowns = {}
            
            # Stats
            self.stats = {
                'total_messages': 0,
                'total_roasts': 0,
                'total_errors': 0,
                'start_time': datetime.now()
            }
            
            # Random styles (keep these in bot.py)
            self.border_styles = self._get_border_styles()
            self.word_variations = self._get_word_variations()
            
            self.logger.info("✅ RoastifyBot (Dynamic) initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize bot: {e}")
            traceback.print_exc()
            raise
    
    def _setup_module_shortcuts(self):
        """সাধারণভাবে ব্যবহৃত মডিউলগুলোর শর্টকাট সেটআপ করুন"""
        # Core modules
        self.logger = self.modules.get('logger')
        self.time_manager = self.modules.get('time_manager')
        self.helpers = self.modules.get('helpers')
        self.text_processor = self.modules.get('text_processor')
        
        # Roast engine
        self.roast_engine = self.modules.get('roast_engine')
        self.safety_checker = self.modules.get('safety_checker')
        
        # Image engine
        self.image_generator = self.modules.get('image_generator')
        
        # Feature systems
        self.welcome_system = self.modules.get('welcome_system')
        self.vote_system = self.modules.get('vote_system')
        self.mention_system = self.modules.get('mention_system')
        self.reaction_system = self.modules.get('reaction_system')
        self.admin_protection = self.modules.get('admin_protection')
        self.sticker_maker = self.modules.get('sticker_maker')
        self.quote_of_day = self.modules.get('quote_of_day')
    
    def _get_border_styles(self):
        """বর্ডার স্টাইলস"""
        return {
            "fire": {"top": "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥", "bottom": "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥"},
            "star": {"top": "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦", "bottom": "✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦✦"},
            "heart": {"top": "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️", "bottom": "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️"},
            "diamond": {"top": "💎💎💎💎💎💎💎💎💎💎", "bottom": "💎💎💎💎💎💎💎💎💎💎"},
        }
    
    def _get_word_variations(self):
        """শব্দ ভেরিয়েশন"""
        return {
            "welcome": ["স্বাগতম", "আসসালামু আলাইকুম", "Welcome"],
            "help": ["সাহায্য", "হেল্প", "গাইড"],
            "roast": ["রোস্ট", "মজা", "জোক"],
            "funny": ["মজার", "হাসির", "কৌতুক"],
            # ... বাকি সব
        }
    
    # ==================== COMMAND HANDLERS ====================
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start command"""
        try:
            user = update.effective_user
            
            # Log user
            if self.logger:
                self.logger.info(f"User {user.id} started the bot")
            
            # Send welcome message
            welcome_text = f"হ্যালো {user.first_name}! 😊\n\n"
            welcome_text += "আমি রোস্টিফাই বট। মেসেজ লিখলেই রোস্ট পাবেন! 🔥\n\n"
            welcome_text += "কমান্ডস:\n"
            welcome_text += "/help - সাহায্য\n"
            welcome_text += "/roast - র‍্যান্ডম রোস্ট\n"
            welcome_text += "/quote - আজকের উক্তি\n"
            welcome_text += "/ping - বট চেক\n\n"
            welcome_text += "শুরু করতে একটি মেসেজ লিখুন!"
            
            await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)
            
            self.stats['total_messages'] += 1
            
        except Exception as e:
            error_msg = f"Error in handle_start: {e}"
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(f"❌ {error_msg}")
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/help command"""
        try:
            help_text = "🤖 **রোস্টিফাই বট - হেল্প**\n\n"
            help_text += "**কিভাবে ব্যবহার করবেন:**\n"
            help_text += "১. শুধু একটি মেসেজ লিখুন\n"
            help_text += "২. বট অটোমেটিক রোস্ট জেনারেট করবে\n"
            help_text += "৩. ইমেজ সহ উত্তর পাবেন\n\n"
            
            help_text += "**কমান্ড লিস্ট:**\n"
            help_text += "/start - বট শুরু করুন\n"
            help_text += "/help - এই মেসেজ\n"
            help_text += "/roast - র‍্যান্ডম রোস্ট\n"
            help_text += "/quote - আজকের উক্তি\n"
            help_text += "/ping - বট স্ট্যাটাস চেক\n"
            help_text += "/info - বট তথ্য\n\n"
            
            help_text += "**ফিচারস:**\n"
            help_text += "• ইমেজ জেনারেশন\n"
            help_text += "• বাংলা/ইংরেজি সাপোর্ট\n"
            help_text += "• র‍্যান্ডম টেমপ্লেট\n"
            help_text += "• ভোট সিস্টেম\n"
            
            await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            error_msg = f"Error in handle_help: {e}"
            if self.logger:
                self.logger.error(error_msg)
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """টেক্সট মেসেজ হ্যান্ডলার"""
        try:
            message = update.effective_message
            user = update.effective_user
            
            self.stats['total_messages'] += 1
            
            # Check cooldown
            if not self._check_cooldown(user.id):
                await update.message.reply_text("⏳ একটু অপেক্ষা করুন!", parse_mode=ParseMode.HTML)
                return
            
            # Generate roast
            roast_text = self._generate_roast(message.text, user)
            
            # Send response
            await update.message.reply_text(
                f"🔥 **রোস্ট টাইম!**\n\n{roast_text}\n\n— @{user.username or user.first_name}",
                parse_mode=ParseMode.HTML
            )
            
            self.stats['total_roasts'] += 1
            
            if self.logger:
                self.logger.info(f"Roasted user {user.id}")
                
        except Exception as e:
            self.stats['total_errors'] += 1
            error_msg = f"Error in handle_text_message: {e}"
            if self.logger:
                self.logger.error(error_msg)
            
            await update.message.reply_text("😓 রোস্ট জেনারেট করতে সমস্যা!", parse_mode=ParseMode.HTML)
    
    def _generate_roast(self, text: str, user) -> str:
        """রোস্ট জেনারেট করুন"""
        if self.roast_engine:
            try:
                return self.roast_engine.generate_roast(text, user.id)
            except:
                pass
        
        # Fallback roasts
        roasts = [
            f"ওহো {user.first_name}! তুমি তো মজার! 😂",
            f"{user.first_name}, তোমার জন্য বিশেষ রোস্ট! 🔥",
            f"একটু ভাবছি {user.first_name}... হুমম! 🤔",
            f"রেডি {user.first_name}? এখানে তোমার রোস্ট! 🎯",
        ]
        
        return random.choice(roasts)
    
    def _check_cooldown(self, user_id: int) -> bool:
        """কুলডাউন চেক করুন"""
        current_time = datetime.now()
        
        if user_id in self.user_cooldowns:
            last_time = self.user_cooldowns[user_id]
            time_diff = (current_time - last_time).total_seconds()
            
            if time_diff < 5:  # 5 seconds cooldown
                return False
        
        self.user_cooldowns[user_id] = current_time
        return True
    
    # ==================== BOT CONTROL ====================
    
    def setup_application(self):
        """টেলিগ্রাম অ্যাপ্লিকেশন সেটআপ"""
        try:
            self.application = (
                ApplicationBuilder()
                .token(Config.BOT_TOKEN)
                .concurrent_updates(True)
                .build()
            )
            
            # Register handlers
            self._register_handlers()
            
            return True
            
        except Exception as e:
            error_msg = f"Application setup failed: {e}"
            if self.logger:
                self.logger.error(error_msg)
            return False
    
    def _register_handlers(self):
        """হ্যান্ডলার রেজিস্টার করুন"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("roast", self.handle_start))
        self.application.add_handler(CommandHandler("quote", self.handle_start))
        self.application.add_handler(CommandHandler("ping", self.handle_start))
        self.application.add_handler(CommandHandler("info", self.handle_start))
        
        # Text message handler
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_message
        ))
        
        if self.logger:
            self.logger.info("✅ Handlers registered successfully")
    
    async def run(self):
        """বট রান করুন"""
        try:
            print("🚀 Starting Roastify Bot...")
            
            if not self.setup_application():
                raise Exception("Failed to setup application")
            
            # Get bot info
            bot_info = await self.application.bot.get_me()
            print(f"🤖 Bot Info: @{bot_info.username} (ID: {bot_info.id})")
            
            if self.logger:
                self.logger.info(f"Bot started: @{bot_info.username}")
            
            # Start
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            print("✅ Bot started successfully!")
            print("📡 Listening for messages...")
            
            self.is_running = True
            
            # Keep running
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            error_msg = f"Failed to start bot: {e}"
            print(f"❌ {error_msg}")
            if self.logger:
                self.logger.error(error_msg)
            await self.stop()
    
    async def stop(self):
        """বট স্টপ করুন"""
        try:
            self.is_running = False
            
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            print("✅ Bot stopped successfully")
            
        except Exception as e:
            error_msg = f"Error stopping bot: {e}"
            print(f"❌ {error_msg}")


# ==================== MAIN FUNCTION ====================

async def main():
    """মেইন ফাংশন"""
    try:
        print("\n" + "="*50)
        print("🤖 ROASTIFY BOT - DYNAMIC MODULE LOADING")
        print("="*50 + "\n")
        
        # Create and run bot
        bot = RoastifyBot()
        await bot.run()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
    finally:
        print("\n👋 Thank you for using Roastify Bot!")


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
