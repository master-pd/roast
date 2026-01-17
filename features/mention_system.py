from typing import Dict, List, Optional, Set
from telegram import Update, User
from telegram.ext import ContextTypes
from config import Config
from utils.logger import logger
from utils.text_processor import TextProcessor
from database.storage import StorageManager
from roast_engine.roaster import RoastEngine
from image_engine.image_generator import ImageGenerator

class MentionSystem:
    def __init__(self):
        self.roast_engine = RoastEngine()
        self.image_generator = ImageGenerator()
        self.text_processor = TextProcessor()
        
    async def handle_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """মেনশন হ্যান্ডল করে"""
        message = update.effective_message
        chat = update.effective_chat
        user = update.effective_user
        
        if not message or not chat or not user:
            return False
        
        # Check if in group/supergroup
        if chat.type not in ["group", "supergroup"]:
            return False
        
        # Check if bot is mentioned
        if Config.BOT_USERNAME.lower() not in message.text.lower():
            return False
        
        # Extract mentioned users
        mentioned_users = self._extract_mentions(message.text)
        
        # Remove bot from mentions
        bot_mentions = [m for m in mentioned_users if Config.BOT_USERNAME.lower() in m.lower()]
        if not bot_mentions:
            return False
        
        # Get the main mentioned user (not the sender)
        target_user = self._get_target_user(message, user.id)
        
        if target_user:
            return await self._roast_mentioned_user(update, context, target_user, user)
        else:
            return await self._roast_general_mention(update, context, user)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """টেক্সট থেকে মেনশন এক্সট্র্যাক্ট করে"""
        import re
        mentions = re.findall(r'@(\w+)', text)
        return [m.lower() for m in mentions]
    
    def _get_target_user(self, message, sender_id: int) -> Optional[User]:
        """টার্গেট ইউজার বের করে"""
        if not message.entities:
            return None
        
        for entity in message.entities:
            if entity.type == "text_mention" and entity.user:
                mentioned_user = entity.user
                # Exclude sender and bots
                if mentioned_user.id != sender_id and not mentioned_user.is_bot:
                    return mentioned_user
        
        return None
    
    async def _roast_mentioned_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   target_user: User, sender: User) -> bool:
        """মেনশন করা ইউজারকে রোস্ট করে"""
        try:
            # Generate targeted roast
            roast_data = self.roast_engine.generate_targeted_roast(
                target_name=target_user.first_name,
                sender_name=sender.first_name
            )
            
            # Create image
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=target_user.id
            )
            
            # Save and send image
            image_path = self.image_generator.save_image(
                image, 
                f"mention_{target_user.id}_{sender.id}.png"
            )
            
            caption = f"🎯 {target_user.first_name} - লক্ষ্যবস্তু! 😏"
            
            with open(image_path, 'rb') as photo:
                sent_message = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=caption,
                    reply_to_message_id=update.effective_message.message_id
                )
            
            # Log the roast
            StorageManager.log_roast(
                user_id=target_user.id,
                input_text=f"Mentioned by {sender.id}",
                roast_type="targeted",
                template_used="mention_template",
                chat_id=update.effective_chat.id
            )
            
            # Add reactions
            await self._add_mention_reactions(context, sent_message)
            
            logger.info(f"Roasted mentioned user {target_user.id} by {sender.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error roasting mentioned user: {e}")
            return False
    
    async def _roast_general_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    sender: User) -> bool:
        """সাধারণ মেনশন রোস্ট করে"""
        try:
            # Get message text without mentions
            text = update.effective_message.text
            text = text.replace(f"@{Config.BOT_USERNAME}", "").strip()
            
            if not text or len(text) < Config.MIN_INPUT_LENGTH:
                # Just acknowledge mention
                roast_data = {
                    "primary": f"হ্যালো {sender.first_name}!",
                    "secondary": "আমাকে ডেকেছ? 😏",
                    "category": "neutral",
                    "emoji": "👋"
                }
            else:
                # Roast based on text
                roast_data = self.roast_engine.generate_roast(text, sender.id)
            
            # Create image
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=sender.id
            )
            
            image_path = self.image_generator.save_image(image)
            
            with open(image_path, 'rb') as photo:
                sent_message = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    reply_to_message_id=update.effective_message.message_id
                )
            
            # Log the roast
            StorageManager.log_roast(
                user_id=sender.id,
                input_text=text[:100],
                roast_type=roast_data["category"],
                template_used="general_mention",
                chat_id=update.effective_chat.id
            )
            
            logger.info(f"Responded to mention from {sender.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling general mention: {e}")
            return False
    
    async def _add_mention_reactions(self, context: ContextTypes.DEFAULT_TYPE, message):
        """মেনশন মেসেজে রিএকশন অ্যাড করে"""
        try:
            reactions = ["🎯", "😂", "🔥", "😏"]
            selected = reactions[:3]  # First 3 reactions
            
            for reaction in selected:
                await context.bot.set_message_reaction(
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    reaction=[{"type": "emoji", "emoji": reaction}]
                )
                import asyncio
                await asyncio.sleep(0.3)
                
        except Exception as e:
            logger.error(f"Error adding mention reactions: {e}")
    
    async def handle_multiple_mentions(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                      mentioned_users: List[User]) -> bool:
        """একাধিক মেনশন হ্যান্ডল করে"""
        if len(mentioned_users) > 3:
            # Too many mentions, respond generally
            roast_data = {
                "primary": "অনেকজনকে ডাকছ! 😅",
                "secondary": "একবারে একজনকেই রোস্ট করি! 😏",
                "category": "neutral",
                "emoji": "🙈"
            }
        else:
            # Roast each mentioned user
            names = ", ".join([user.first_name for user in mentioned_users])
            roast_data = {
                "primary": f"{names} - সবাই একসাথে! 🎯",
                "secondary": "গ্রুপ রোস্টের সময়! 🔥",
                "category": "targeted",
                "emoji": "👥"
            }
        
        try:
            image = self.image_generator.create_roast_image(
                primary_text=roast_data["primary"],
                secondary_text=roast_data["secondary"],
                user_id=update.effective_user.id
            )
            
            image_path = self.image_generator.save_image(image)
            
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    reply_to_message_id=update.effective_message.message_id
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling multiple mentions: {e}")
            return False