import random
from typing import Dict, List, Set
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager
from utils.text_processor import TextProcessor
from database.storage import StorageManager

class ReactionSystem:
    def __init__(self):
        self.text_processor = TextProcessor()
        
        # Track user reaction cooldowns
        self.user_cooldowns = {}  # user_id -> last_reaction_time
        
        # Reaction combos
        self.reaction_combos = {
            "funny": [["😂", "🤣", "😭"], ["🤣", "👏", "🎉"]],
            "sad": [["😢", "😭", "🤗"], ["☹️", "😔", "❤️"]],
            "love": [["❤️", "😍", "🥰"], ["💖", "😘", "💕"]],
            "motivation": [["💪", "🔥", "🚀"], ["🏆", "⭐", "✨"]],
            "attitude": [["😎", "🤘", "👑"], ["😏", "💥", "⚡"]],
            "neutral": [["👍", "👀", "🤔"], ["😄", "🙂", "👌"]]
        }
        
        # Special combos for high intensity
        self.special_combos = [
            ["🔥", "💀", "⚡"],  # Savage combo
            ["🎊", "🎉", "🎈"],  # Celebration combo
            ["🤯", "😱", "🙀"]   # Shocked combo
        ]
    
    async def analyze_and_react(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """মেসেজ অ্যানালাইজ করে রিএকশন দেয়"""
        message = update.effective_message
        user = update.effective_user
        chat = update.effective_chat
        
        if not message or not message.text:
            return False
        
        # Check cooldown for user
        if not self._check_cooldown(user.id):
            return False
        
        # Check message length
        if len(message.text) < Config.MIN_INPUT_LENGTH:
            return False
        
        # Ignore certain messages
        if self._should_ignore_message(message):
            return False
        
        # Analyze text
        topics = self.text_processor.detect_topic(message.text)
        mood = self.text_processor.analyze_mood(message.text)
        
        # Select reaction combo
        combo = self._select_reaction_combo(topics, mood)
        
        if not combo:
            return False
        
        try:
            # Send reactions
            for emoji in combo:
                await context.bot.set_message_reaction(
                    chat_id=chat.id,
                    message_id=message.message_id,
                    reaction=[{"type": "emoji", "emoji": emoji}]
                )
                # Small delay between reactions
                import asyncio
                await asyncio.sleep(0.5)
            
            # Update cooldown
            self.user_cooldowns[user.id] = TimeManager.get_current_time()
            
            # Log reaction
            StorageManager.increment_user_reaction_count(user.id)
            
            logger.info(f"Added reactions {combo} to message from {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding reactions: {e}")
            return False
    
    def _check_cooldown(self, user_id: int) -> bool:
        """রিএকশন কুলডাউন চেক করে"""
        if user_id not in self.user_cooldowns:
            return True
        
        last_reaction = self.user_cooldowns[user_id]
        time_diff = (TimeManager.get_current_time() - last_reaction).total_seconds()
        
        return time_diff >= Config.REACTION_COOLDOWN
    
    def _should_ignore_message(self, message) -> bool:
        """মেসেজ ইগনোর করা উচিত কিনা"""
        text = message.text.lower()
        
        # Ignore very short messages
        if len(text) < 5:
            return True
        
        # Ignore messages with only links
        if "http://" in text or "https://" in text:
            if len(text.replace("http://", "").replace("https://", "").strip()) < 5:
                return True
        
        # Ignore commands
        if text.startswith('/'):
            return True
        
        # Ignore bot mentions only
        if text.strip() == f"@{Config.BOT_USERNAME}".lower():
            return True
        
        return False
    
    def _select_reaction_combo(self, topics: List[str], mood: Dict) -> List[str]:
        """রিএকশন কম্বো সিলেক্ট করে"""
        # Check for high intensity (special combos)
        if mood["intensity"] > 8:
            return random.choice(self.special_combos)
        
        # Select based on primary topic
        primary_topic = topics[0] if topics else "neutral"
        
        if primary_topic in self.reaction_combos:
            combos = self.reaction_combos[primary_topic]
            return random.choice(combos)
        
        # Fallback to neutral
        return random.choice(self.reaction_combos["neutral"])
    
    async def add_targeted_reaction(self, context: ContextTypes.DEFAULT_TYPE,
                                   chat_id: int, message_id: int, 
                                   reaction_type: str = "funny") -> bool:
        """টার্গেটেড রিএকশন অ্যাড করে"""
        try:
            emojis = self._get_reaction_emojis(reaction_type)
            
            for emoji in emojis:
                await context.bot.set_message_reaction(
                    chat_id=chat_id,
                    message_id=message_id,
                    reaction=[{"type": "emoji", "emoji": emoji}]
                )
                import asyncio
                await asyncio.sleep(0.3)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding targeted reaction: {e}")
            return False
    
    def _get_reaction_emojis(self, reaction_type: str) -> List[str]:
        """রিএকশন টাইপ ভিত্তিতে ইমোজি রিটার্ন করে"""
        reaction_map = {
            "funny": ["😂", "🤣", "😹"],
            "sad": ["😢", "😭", "🤗"],
            "love": ["❤️", "😍", "🥰"],
            "motivation": ["💪", "🔥", "🏆"],
            "attitude": ["😎", "🤘", "😏"],
            "congrats": ["🎉", "🎊", "👏"],
            "shocked": ["😱", "🤯", "🙀"],
            "angry": ["😠", "🤬", "💢"]
        }
        
        return reaction_map.get(reaction_type, ["👍", "👏", "🔥"])
    
    def get_user_reaction_stats(self, user_id: int) -> Dict:
        """ইউজারের রিএকশন স্ট্যাট রিটার্ন করে"""
        # This would query database
        return {
            "total_reactions": 0,
            "reactions_today": 0,
            "favorite_emoji": "👍",
            "reaction_streak": 0
        }
    
    def reset_cooldowns(self):
        """সকল কুলডাউন রিসেট করে"""
        old_count = len(self.user_cooldowns)
        current_time = TimeManager.get_current_time()
        
        # Remove old cooldowns (older than 1 hour)
        to_remove = []
        for user_id, last_time in self.user_cooldowns.items():
            time_diff = (current_time - last_time).total_seconds()
            if time_diff > 3600:  # 1 hour
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.user_cooldowns[user_id]
        
        logger.info(f"Reset {len(to_remove)} cooldowns, remaining: {len(self.user_cooldowns)}")