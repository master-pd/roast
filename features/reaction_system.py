"""
Reaction System for Roastify Bot
Fully Fixed
"""

import random
from typing import Dict, List
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from utils.logger import logger
from utils.time_manager import TimeManager
from utils.text_processor import TextProcessor

class ReactionSystem:
    """রিএকশন সিস্টেম ক্লাস - সম্পূর্ণ ফিক্সড"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.user_cooldowns = {}
        
        # Reaction combos
        self.reaction_combos = {
            "funny": [["😂", "🤣"], ["😄", "👏"]],
            "sad": [["😢", "🤗"], ["😔", "❤️"]],
            "love": [["❤️", "😍"], ["💖", "🥰"]],
            "motivation": [["💪", "🔥"], ["🏆", "🚀"]],
            "attitude": [["😎", "🤘"], ["😏", "👑"]],
            "neutral": [["👍", "👀"], ["😊", "👌"]]
        }
    
    async def analyze_and_react(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """মেসেজ অ্যানালাইজ করে রিএকশন দেয় - ফিক্সড"""
        message = update.effective_message
        user = update.effective_user
        
        if not message or not message.text:
            return False
        
        # Check cooldown for user
        if not self._check_cooldown(user.id):
            return False
        
        # Check minimum length
        if len(message.text) < getattr(Config, 'MIN_INPUT_LENGTH', 4):
            return False
        
        # Analyze text
        topics = self.text_processor.detect_topic(message.text)
        
        # Select reaction combo
        combo = self._select_reaction_combo(topics)
        
        if not combo:
            return False
        
        try:
            # Send reactions with correct format
            for emoji in combo:
                try:
                    await context.bot.set_message_reaction(
                        chat_id=message.chat_id,
                        message_id=message.message_id,
                        reaction=[{"type": "emoji", "emoji": emoji}]
                    )
                    # Small delay
                    import asyncio
                    await asyncio.sleep(0.3)
                except Exception as e:
                    logger.warning(f"Could not add reaction {emoji}: {e}")
            
            # Update cooldown
            self.user_cooldowns[user.id] = TimeManager.get_current_time()
            
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
        
        cooldown = getattr(Config, 'REACTION_COOLDOWN', 15)
        return time_diff >= cooldown
    
    def _select_reaction_combo(self, topics: List[str]) -> List[str]:
        """রিএকশন কম্বো সিলেক্ট করে"""
        if not topics:
            return random.choice(self.reaction_combos["neutral"])
        
        # Use primary topic
        primary_topic = topics[0]
        
        if primary_topic in self.reaction_combos:
            combos = self.reaction_combos[primary_topic]
            return random.choice(combos)
        
        # Fallback
        return random.choice(self.reaction_combos["neutral"])
    
    def reset_cooldowns(self):
        """কুলডাউন রিসেট করে"""
        old_count = len(self.user_cooldowns)
        
        # Remove old cooldowns (older than 1 hour)
        current_time = TimeManager.get_current_time()
        to_remove = []
        
        for user_id, last_time in self.user_cooldowns.items():
            time_diff = (current_time - last_time).total_seconds()
            if time_diff > 3600:  # 1 hour
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.user_cooldowns[user_id]
        
        logger.info(f"Reset {len(to_remove)} cooldowns, remaining: {len(self.user_cooldowns)}")
