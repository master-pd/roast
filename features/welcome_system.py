import random
from typing import Dict, List, Optional
from telegram import Update, Chat, ChatMember, ChatMemberUpdated
from telegram.ext import ContextTypes
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager
from database.storage import StorageManager
from image_engine.image_generator import ImageGenerator

class WelcomeSystem:
    def __init__(self):
        self.image_generator = ImageGenerator()
        self.welcome_messages = Config.WELCOME_MESSAGES
        
        # Different welcome types
        self.welcome_types = {
            "bot_start": [
                "স্বাগতম! রোস্টের জন্য প্রস্তুত? 😈",
                "বট চালু হয়েছে! এখন অপমানের পালা! 😏",
                "হ্যালো! আমাকে নিয়ে গ্রুপে যুক্ত করো! 👋"
            ],
            "group_add": [
                "ধন্যবাদ আমাকে গ্রুপে যুক্ত করার জন্য! 😊",
                "গ্রুপে যুক্ত হওয়ায় আনন্দিত! এখন রোস্ট শুরু! 🔥",
                "নতুন গ্রুপ, নতুন শিকার! 😈"
            ],
            "new_member": [
                "অভিনন্দন {}! গ্রুপে স্বাগতম! 🎉",
                "হ্যালো {}! আমাকে মনে রাখবে! 😏",
                "{} এসেছে! এবার রোস্টের পালা! 🔥"
            ],
            "returning_member": [
                "ওহো {} ফিরেছে! আবার অপমান শুরু! 😄",
                "{} আবারও গ্রুপে যোগ দিল! প্রস্তুত হও! 🚀",
                "ফিরে আসায় স্বাগতম {}! এবার কিছু মজা করি! 😈"
            ]
        }
    
    async def handle_bot_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """বট স্টার্ট হলে ওয়েলকাম মেসেজ"""
        user = update.effective_user
        
        # Get random welcome message
        welcome_msg = random.choice(self.welcome_types["bot_start"])
        
        # Create welcome image
        roast_data = {
            "primary": f"স্বাগতম {user.first_name}!",
            "secondary": welcome_msg,
            "category": "neutral",
            "emoji": "👋"
        }
        
        try:
            # Generate image
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=user.id
            )
            
            # Save image
            image_path = self.image_generator.save_image(image)
            
            # Send message with image
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=user.id,
                    photo=photo,
                    caption=f"🤖 @{Config.BOT_USERNAME} চালু হয়েছে!\n\n{welcome_msg}"
                )
            
            logger.info(f"Sent welcome to user {user.id}")
            
        except Exception as e:
            logger.error(f"Error sending welcome: {e}")
            # Fallback to text message
            await update.message.reply_text(f"👋 হ্যালো {user.first_name}!\n\n{welcome_msg}")
    
    async def handle_bot_added_to_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """বট গ্রুপে অ্যাড হলে"""
        chat = update.effective_chat
        
        if not chat:
            return
        
        # Store chat info
        StorageManager.get_or_create_chat(
            chat_id=chat.id,
            chat_type=chat.type,
            title=chat.title
        )
        
        # Get welcome message
        welcome_msg = random.choice(self.welcome_types["group_add"])
        
        try:
            # Create group welcome image
            image = self.image_generator.create_roast_image(
                primary_text=f"গ্রুপে স্বাগতম!",
                secondary_text=welcome_msg,
                user_id=chat.id
            )
            
            image_path = self.image_generator.save_image(image)
            
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat.id,
                    photo=photo,
                    caption=f"🤖 @{Config.BOT_USERNAME} গ্রুপে যোগ দিয়েছে!\n\n{welcome_msg}\n\n📝 নিয়ম: মেসেজ লিখলে রোস্ট ইমেজ পাবে!"
                )
            
            logger.info(f"Bot added to group {chat.id}")
            
        except Exception as e:
            logger.error(f"Error sending group welcome: {e}")
            await update.message.reply_text(
                f"🤖 @{Config.BOT_USERNAME} গ্রুপে যোগ দিয়েছে!\n\n{welcome_msg}"
            )
    
    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """নতুন মেম্বার জয়েন করলে"""
        chat = update.effective_chat
        
        if not chat:
            return
        
        # Check if bot itself was added
        new_members = update.message.new_chat_members
        for member in new_members:
            if member.id == context.bot.id:
                # Bot was added, handle separately
                await self.handle_bot_added_to_group(update, context)
                return
        
        # For other new members
        for member in new_members:
            # Skip if member is a bot
            if member.is_bot:
                continue
            
            # Get or create user in database
            StorageManager.get_or_create_user(
                user_id=member.id,
                username=member.username,
                first_name=member.first_name,
                last_name=member.last_name
            )
            
            # Check if returning member
            is_returning = await self._is_returning_member(member.id, chat.id)
            
            if is_returning:
                welcome_type = "returning_member"
            else:
                welcome_type = "new_member"
            
            # Get welcome message
            template = random.choice(self.welcome_types[welcome_type])
            welcome_msg = template.format(member.first_name)
            
            try:
                # Create welcome image
                image = self.image_generator.create_roast_image(
                    primary_text=f"স্বাগতম {member.first_name}!",
                    secondary_text=welcome_msg,
                    user_id=member.id
                )
                
                image_path = self.image_generator.save_image(image)
                
                with open(image_path, 'rb') as photo:
                    sent_message = await context.bot.send_photo(
                        chat_id=chat.id,
                        photo=photo,
                        caption=f"👋 {welcome_msg}"
                    )
                
                logger.info(f"Sent welcome to {member.id} in chat {chat.id}")
                
                # Add reaction to welcome message
                await self._add_welcome_reactions(context, chat.id, sent_message.message_id)
                
            except Exception as e:
                logger.error(f"Error welcoming member {member.id}: {e}")
                # Fallback to simple text
                await update.message.reply_text(f"👋 {welcome_msg}")
    
    async def _is_returning_member(self, user_id: int, chat_id: int) -> bool:
        """মেম্বার রিটার্নিং কিনা চেক করে"""
        # This would check database for previous membership
        # For now, simple implementation
        return False
    
    async def _add_welcome_reactions(self, context: ContextTypes.DEFAULT_TYPE, 
                                    chat_id: int, message_id: int):
        """ওয়েলকাম মেসেজে রিএকশন অ্যাড করে"""
        try:
            reactions = ["👋", "🎉", "🔥", "😊", "🤗"]
            selected_reactions = random.sample(reactions, min(3, len(reactions)))
            
            for reaction in selected_reactions:
                await context.bot.set_message_reaction(
                    chat_id=chat_id,
                    message_id=message_id,
                    reaction=[{"type": "emoji", "emoji": reaction}]
                )
                # Small delay between reactions
                import asyncio
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error adding reactions: {e}")
    
    async def send_custom_welcome(self, chat_id: int, user_name: str, 
                                 welcome_type: str = "custom") -> bool:
        """কাস্টম ওয়েলকাম মেসেজ পাঠায়"""
        try:
            messages = {
                "custom": f"স্বাগতম {user_name}! গ্রুপে আনন্দে থাকো! 😊",
                "special": f"🎊 বিশেষ স্বাগতম {user_name}! 🎊",
                "admin": f"অভ্যর্থনা {user_name}! আপনি অ্যাডমিন প্যানেলে যুক্ত হয়েছেন! 👑"
            }
            
            message = messages.get(welcome_type, messages["custom"])
            
            image = self.image_generator.create_roast_image(
                primary_text=f"স্বাগতম {user_name}!",
                secondary_text=message,
                user_id=chat_id  # Using chat_id as user_id for uniqueness
            )
            
            image_path = self.image_generator.save_image(image)
            
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=message
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending custom welcome: {e}")
            return False