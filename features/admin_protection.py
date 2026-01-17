from typing import Dict, List, Set
from telegram import Update, User
from telegram.ext import ContextTypes
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager
from roast_engine.roaster import RoastEngine
from roast_engine.safety_check import SafetyChecker
from image_engine.image_generator import ImageGenerator

class AdminProtection:
    def __init__(self):
        self.roast_engine = RoastEngine()
        self.safety_checker = SafetyChecker()
        self.image_generator = ImageGenerator()
        
        # Track cooldowns for protected users
        self.protection_cooldowns = {}  # user_id -> last_protection_time
        
        # Protection responses
        self.protection_responses = [
            {
                "primary": "ওহো! ওনার/অ্যাডমিনকে ডিস্টার্ব করছ? 😳",
                "secondary": "একটু সতর্ক হও! ⚠️",
                "category": "warning"
            },
            {
                "primary": "এটা ভালো আইডিয়া না! 🙅",
                "secondary": "ওনার/অ্যাডমিন রাগ করবে! 😬",
                "category": "warning"
            },
            {
                "primary": "থামো! এটা করো না! ✋",
                "secondary": "বট ওনারকে অপমান করো না! 😠",
                "category": "strict"
            }
        ]
    
    async def check_and_protect(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """মেসেজ চেক করে প্রটেকশন দেয়"""
        message = update.effective_message
        user = update.effective_user
        
        if not message or not message.text:
            return False
        
        # Check if message targets owner/admin
        if not self._is_targeting_protected_user(message.text, user.id):
            return False
        
        # Check cooldown
        if not self._check_protection_cooldown(user.id):
            return False
        
        # Generate protection response
        return await self._send_protection_response(update, context, user)
    
    def _is_targeting_protected_user(self, text: str, sender_id: int) -> bool:
        """মেসেজ প্রটেক্টেড ইউজারকে টার্গেট করছে কিনা"""
        # Check for trigger words
        if not self.safety_checker.check_for_trigger_words(text):
            return False
        
        # Check if sender is not owner/admin (they can't target themselves)
        if self.safety_checker.is_owner_or_admin(sender_id):
            return False
        
        # Check for owner/admin mentions
        text_lower = text.lower()
        
        # Check for direct mentions
        owner_mentions = ["ওনার", "মালিক", "ক্রিয়েটর", "বস"]
        admin_mentions = ["অ্যাডমিন", "এডমিন", "মডারেটর"]
        
        for mention in owner_mentions + admin_mentions:
            if mention in text_lower:
                return True
        
        # Check for angry/abusive tone towards authority
        angry_words = ["খারাপ", "গালি", "অপমান", "বোকা", "নষ্ট"]
        authority_words = ["ওনার", "অ্যাডমিন", "বট"]
        
        has_angry = any(word in text_lower for word in angry_words)
        has_authority = any(word in text_lower for word in authority_words)
        
        return has_angry and has_authority
    
    def _check_protection_cooldown(self, user_id: int) -> bool:
        """প্রটেকশন কুলডাউন চেক করে"""
        if user_id not in self.protection_cooldowns:
            return True
        
        last_protection = self.protection_cooldowns[user_id]
        time_diff = (TimeManager.get_current_time() - last_protection).total_seconds()
        
        return time_diff >= Config.COOLDOWN_SECONDS
    
    async def _send_protection_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                       sender: User) -> bool:
        """প্রটেকশন রেস্পন্স পাঠায়"""
        try:
            # Select protection response
            response = self._select_protection_response(sender.id)
            
            # Create protection image
            image = self.image_generator.create_roast_image(
                primary_text=response["primary"],
                secondary_text=response["secondary"],
                user_id=sender.id
            )
            
            image_path = self.image_generator.save_image(
                image, 
                f"protection_{sender.id}.png"
            )
            
            caption = "⚠️ সতর্কতা: ওনার/অ্যাডমিনকে ডিস্টার্ব করো না!"
            
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=caption,
                    reply_to_message_id=update.effective_message.message_id
                )
            
            # Update cooldown
            self.protection_cooldowns[sender.id] = TimeManager.get_current_time()
            
            # Log the protection action
            logger.warning(f"Protected admin from user {sender.id}")
            
            # Notify owner/admin if needed
            await self._notify_owner(context, sender, update.effective_message.text)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending protection response: {e}")
            return False
    
    def _select_protection_response(self, user_id: int) -> Dict:
        """প্রটেকশন রেস্পন্স সিলেক্ট করে"""
        # Check user's violation history
        violation_count = self._get_violation_count(user_id)
        
        if violation_count > 3:
            # Strict response for repeat offenders
            return {
                "primary": "বারবার সতর্ক করা হচ্ছে! ⚠️",
                "secondary": "আর করলে রিপোর্ট করা হবে! 🚫",
                "category": "strict"
            }
        elif violation_count > 1:
            # Medium response
            return {
                "primary": "আবারও! সতর্ক থাকো! 😠",
                "secondary": "একটু ভদ্রভাবে কথা বলো! 🙏",
                "category": "warning"
            }
        else:
            # First offense, gentle response
            return random.choice(self.protection_responses)
    
    def _get_violation_count(self, user_id: int) -> int:
        """ইউজারের ভায়োলেশন কাউন্ট রিটার্ন করে"""
        # This would query database
        # Simplified implementation
        return 0
    
    async def _notify_owner(self, context: ContextTypes.DEFAULT_TYPE, 
                           violator: User, violation_text: str):
        """ওনারকে নোটিফাই করে"""
        try:
            if Config.OWNER_ID:
                message = (
                    f"⚠️ অ্যাডমিন প্রটেকশন অ্যালার্ট!\n\n"
                    f"ইউজার: {violator.first_name} (@{violator.username or 'N/A'})\n"
                    f"ID: {violator.id}\n"
                    f"মেসেজ: {violation_text[:100]}...\n\n"
                    f"স্বয়ংক্রিয়ভাবে হ্যান্ডল করা হয়েছে।"
                )
                
                await context.bot.send_message(
                    chat_id=Config.OWNER_ID,
                    text=message
                )
                
                logger.info(f"Notified owner about violation by {violator.id}")
                
        except Exception as e:
            logger.error(f"Error notifying owner: {e}")
    
    async def handle_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  command: str, args: List[str] = None) -> bool:
        """অ্যাডমিন কমান্ড হ্যান্ডল করে"""
        user = update.effective_user
        
        if not self.safety_checker.is_owner_or_admin(user.id):
            await update.message.reply_text("⚠️ এই কমান্ড শুধুমাত্র অ্যাডমিনদের জন্য!")
            return False
        
        if command == "protect_stats":
            return await self._show_protection_stats(update, context)
        elif command == "reset_cooldowns":
            return await self._reset_all_cooldowns(update, context)
        elif command == "violation_list":
            return await self._show_violation_list(update, context)
        
        return False
    
    async def _show_protection_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """প্রটেকশন স্ট্যাট দেখায়"""
        try:
            stats = (
                f"🛡️ অ্যাডমিন প্রটেকশন স্ট্যাটস:\n\n"
                f"• একটিভ কুলডাউন: {len(self.protection_cooldowns)}\n"
                f"• টোটাল প্রটেকশন: {sum(self._get_violation_count(uid) for uid in self.protection_cooldowns)}\n"
                f"• সর্বশেষ অ্যাকশন: {TimeManager.format_time()}\n\n"
                f"কমান্ডস:\n"
                f"/reset_cooldowns - সব কুলডাউন রিসেট\n"
                f"/violation_list - ভায়োলেশন লিস্ট"
            )
            
            await update.message.reply_text(stats)
            return True
            
        except Exception as e:
            logger.error(f"Error showing protection stats: {e}")
            return False
    
    async def _reset_all_cooldowns(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """সকল কুলডাউন রিসেট করে"""
        old_count = len(self.protection_cooldowns)
        self.protection_cooldowns.clear()
        
        await update.message.reply_text(
            f"✅ {old_count} টি কুলডাউন রিসেট করা হয়েছে!"
        )
        
        logger.info(f"Admin {update.effective_user.id} reset all cooldowns")
        return True
    
    async def _show_violation_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """ভায়োলেশন লিস্ট দেখায়"""
        # This would show violations from database
        # Simplified version
        message = (
            "📋 ভায়োলেশন লিস্ট:\n\n"
            "ডাটাবেস সংযুক্ত না থাকায় লিস্ট দেখানো যাচ্ছে না।\n"
            "পরবর্তী আপডেটে এই ফিচার যুক্ত হবে।"
        )
        
        await update.message.reply_text(message)
        return True